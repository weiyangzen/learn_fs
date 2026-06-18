# Research: subset-b-006115

Grouped research for the kernel compression sources under `sources/distributed-fs/ceph-client/lib`. Each section is delimited for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_deflate/deflate.c -->
# sources/distributed-fs/ceph-client/lib/zlib_deflate/deflate.c

Purpose: Implements the kernel zlib deflate compressor entry points over a caller-provided `z_stream` and preallocated workspace. It is a Linux-adapted zlib deflater: no internal allocation, optional raw deflate when `windowBits` is negative, normal zlib header/trailer handling otherwise, and optional s390 DFLTCC hardware hook points compiled through `CONFIG_ZLIB_DFLTCC`.

Important APIs/functions:
- `zlib_deflateInit2()` validates level, method, window bits, memory level, and strategy; lays out `struct deflate_workspace` into state, window, hash tables, and pending/literal/distance overlays; then calls reset.
- `zlib_deflateReset()` clears counters and pending output, initializes tree/LZ state, and invokes `DEFLATE_RESET_HOOK()`.
- `zlib_deflate()` is the public streaming compressor. It emits headers/trailers, flushes pending bytes, dispatches to DFLTCC or software compression, handles zlib flush modes, and returns zlib status codes.
- `zlib_deflateEnd()` validates final state and detaches `strm->state`.
- `zlib_deflate_workspacesize()` computes the exact caller workspace size for the selected window and memory level.
- `zlib_deflate_dfltcc_enabled()` exposes whether the compiled DFLTCC hook can be active.

Control flow:
- Initialization stores all mutable state inside `strm->workspace`; no allocator is called here.
- `zlib_deflate()` rejects invalid stream/flush combinations, emits the zlib header on `INIT_STATE`, then drains `pending_buf` before doing new work.
- For block processing, `DEFLATE_HOOK(strm, flush, &bstate)` gets first chance. If DFLTCC declines or is unavailable, the level-indexed `configuration_table` chooses `deflate_stored()`, `deflate_fast()`, or `deflate_slow()`.
- `deflate_stored()` copies input into stored blocks. `deflate_fast()` performs hash-chain matching without lazy evaluation. `deflate_slow()` performs lazy match evaluation and can replace a previous short match with a literal if the next position is better.
- `fill_window()` keeps at least `MIN_LOOKAHEAD` where possible, slides the 2x window, and rewrites hash heads/prev links when the window advances.
- Final flush writes the Adler-32 trailer unless raw mode is active, and marks `noheader = -1` to avoid duplicate trailers.

State and persistence:
- Persistent stream state is `deflate_state` stored in the caller workspace. It tracks pending output, stream status, hash chains, sliding window, match state, Huffman trees, bit buffer, and checksum state through `strm->adler`.
- No on-disk persistence. Static data is limited to the constant compression configuration table; Huffman static tables live in `deftree.c`.
- DFLTCC builds add an adjacent, aligned `struct dfltcc_deflate_state` and page-align the window allocation inside the workspace.

Dependencies and integration:
- Includes `<linux/zutil.h>` and `defutil.h`, with DFLTCC hooks from `../zlib_dfltcc/dfltcc_deflate.h` when configured.
- Calls tree/output helpers from `deftree.c`: `zlib_tr_init`, `zlib_tr_tally`, `zlib_tr_flush_block`, `zlib_tr_align`, `zlib_tr_stored_block`, and `zlib_tr_stored_type_only`.
- Exported by `deflate_syms.c`; kernel consumers include crypto deflate, PowerPC nvram, and device/debug code that allocate `zlib_deflate_workspacesize()` then call the zlib-style API.

Risks:
- The workspace layout is pointer arithmetic over a caller allocation; wrong workspace size or alignment corrupts state. `zlib_deflate_workspacesize()` and DFLTCC page alignment are therefore part of the ABI.
- `zlib_deflate_workspacesize()` uses `BUG_ON()` for invalid parameters because callers commonly pass the result unchecked to allocators; bad user of the helper can panic the kernel.
- `read_buf()` suppresses Adler updates when DFLTCC owns checksumming. Any hook bug can yield checksum divergence.
- `longest_match()` and `fill_window()` are performance- and bounds-sensitive; small off-by-one changes affect compression correctness and history-window safety.

Test signals:
- Round-trip deflate/inflate tests across all levels, raw/zlib wrapper modes, tiny output buffers, and every flush mode.
- Compare compressed output decompression against upstream zlib for deterministic inputs.
- Exercise `Z_FULL_FLUSH` history reset, `Z_PACKET_FLUSH`, and `Z_FINISH` repeated calls.
- On s390, test both hardware-enabled and disabled modes and fallback when parameters are unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_deflate/deflate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_deflate/deflate_syms.c -->
# sources/distributed-fs/ceph-client/lib/zlib_deflate/deflate_syms.c

Purpose: Provides the module symbol exports and metadata for the kernel deflate implementation.

Important APIs/functions:
- Exports `zlib_deflate_workspacesize`, `zlib_deflate_dfltcc_enabled`, `zlib_deflate`, `zlib_deflateInit2`, `zlib_deflateEnd`, and `zlib_deflateReset`.
- Declares module description and GPL license.

Control flow: There is no runtime control flow beyond module metadata registration. The file makes the deflate API available to other built-in or module code through `EXPORT_SYMBOL()`.

State and persistence: No local state. Export table entries become part of the kernel module symbol namespace.

Dependencies and integration:
- Includes `<linux/module.h>`, `<linux/init.h>`, and `<linux/zlib.h>`.
- Integrates `deflate.c` with kernel consumers such as crypto transforms, firmware/debug compression, and architecture-specific code.

Risks:
- Removing or renaming an export breaks out-of-tree or modular in-kernel users.
- Exporting `zlib_deflate_dfltcc_enabled()` exposes architecture acceleration status; behavior must remain stable across build configs.

Test signals:
- Kernel/module build should resolve all exported deflate symbols.
- `modpost` should report no missing or duplicate symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_deflate/deflate_syms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_deflate/deftree.c -->
# sources/distributed-fs/ceph-client/lib/zlib_deflate/deftree.c

Purpose: Builds and emits the Huffman-coded deflate block representation used by `deflate.c`. It manages static tables, dynamic literal/length and distance trees, bit-length trees, stored/static/dynamic block selection, bit emission, and block tallying.

Important APIs/functions:
- `zlib_tr_init()` initializes static tables once, sets tree descriptors, resets bit output state, and starts the first block.
- `zlib_tr_tally()` records literals or length/distance pairs in the overlay buffers and increments frequency counts.
- `zlib_tr_flush_block()` chooses stored, static, or dynamic encoding for the current block and emits it.
- `zlib_tr_align()`, `zlib_tr_stored_block()`, and `zlib_tr_stored_type_only()` implement special flush forms used by `zlib_deflate()`.
- Internal helpers include `tr_static_init()`, `build_tree()`, `gen_bitlen()`, `gen_codes()`, `scan_tree()`, `send_tree()`, `build_bl_tree()`, `send_all_trees()`, `compress_block()`, `set_data_type()`, and `copy_block()`.

Control flow:
- Static initialization builds `length_code`, `dist_code`, base tables, the canonical static literal tree, and the fixed distance tree.
- During compression, `zlib_tr_tally()` accumulates symbols until the literal buffer is full or heuristics say flushing is profitable.
- At block flush, dynamic literal and distance trees are built from frequencies. A bit-length tree is generated to compactly describe the dynamic trees.
- The block decision compares stored length, static tree length, and dynamic tree length. Stored blocks are used when cheaper and the original buffer is still available; otherwise static or dynamic codes are emitted.
- `compress_block()` replays buffered literals/matches through the chosen trees and appends the end-of-block symbol.

State and persistence:
- Uses per-stream `deflate_state` for dynamic tree arrays, heap, frequency counts, bit buffer, pending buffer, and block counters.
- Static tables are file-scope and initialized once; concurrent initialization is intentionally benign because repeated writes compute identical values.
- No external persistence.

Dependencies and integration:
- Includes `<linux/zutil.h>`, `<linux/bitrev.h>`, and `defutil.h`.
- Called only by deflate stream code and DFLTCC code that needs to send software end-of-block bits.
- Depends on `defutil.h` bit-output macros and `flush_pending()` to feed `strm->next_out`.

Risks:
- Huffman tree construction has exact format constraints: at least one distance code, maximum bit lengths, and canonical bit reversal. Changes can create streams other inflaters reject.
- Pending/literal/distance overlays assume average encoded output sizing and buffer invariants; incorrect `lit_bufsize` or `pending` handling can corrupt output.
- Stored block selection requires `buf` to still point to available history; otherwise the code must not choose stored.
- Static initialization lacks locking by design; it is safe only while initialization remains deterministic.

Test signals:
- Deflate conformance against RFC1951 cases: stored, fixed, dynamic, empty, and highly repetitive data.
- Buffer-stress tests with very small output buffers to validate `pending_buf` behavior.
- Fuzz-compress then inflate with independent zlib to catch invalid tree emission.
- Instrumented tests for tree overflow paths in `gen_bitlen()` and bit-length repeat emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_deflate/deftree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_deflate/defutil.h -->
# sources/distributed-fs/ceph-client/lib/zlib_deflate/defutil.h

Purpose: Defines the internal deflate data structures, constants, workspace sizing macros, tree helper prototypes, bit-output helpers, and pending-output flush logic shared by `deflate.c`, `deftree.c`, and DFLTCC deflate glue.

Important APIs/types:
- `ct_data`, `tree_desc`, `deflate_state`, `Pos`, and `IPos` define the compressor state and Huffman tree storage.
- Stream state constants `INIT_STATE`, `BUSY_STATE`, and `FINISH_STATE` track header/body/trailer lifecycle.
- Workspace sizing macros compute window, hash-prev, hash-head, and overlay memory, with DFLTCC window over-allocation for page alignment.
- `MAX_DIST()`, `MIN_LOOKAHEAD`, code-count constants, and buffer constants define deflate format limits.
- Prototypes expose `zlib_tr_*()` helpers implemented in `deftree.c`.
- Inline helpers/macros include `put_byte`, `put_short`, `bi_reverse`, `bi_flush`, `bi_windup`, `send_bits`, `zlib_tr_send_bits`, and `flush_pending`.

Control flow:
- Included by implementation files rather than used directly by external callers.
- `send_bits()` accumulates LSB-first bits into `bi_buf`, flushing full words/bytes into `pending_buf`.
- `flush_pending()` first flushes the bit buffer, then copies pending bytes into `strm->next_out` when non-NULL and updates total output counters.

State and persistence:
- `deflate_state` is the persistent in-memory stream state: pending output, zlib wrapper status, LZ77 window, hash chains, match metadata, compression parameters, Huffman trees, block buffers, and bit buffer.
- No global state here, but consumers rely on the exact `deflate_state` layout for DFLTCC state placement via `GET_DFLTCC_STATE()`.

Dependencies and integration:
- Includes `<linux/zutil.h>`, which provides zlib kernel types and helpers.
- DFLTCC uses `zlib_tr_send_bits()` and `flush_pending()` to mix hardware output with software block-closing bits.
- Public callers should use `<linux/zlib.h>`, not this internal header.

Risks:
- Layout-sensitive: changing `deflate_state` size/alignment affects DFLTCC state placement and workspace sizing.
- `send_bits()` macros evaluate inputs in C macro context and assume lengths/values are valid.
- `flush_pending()` supports `next_out == NULL` only by consuming pending state without writing bytes; callers must understand this behavior.

Test signals:
- Compile with and without `CONFIG_ZLIB_DFLTCC` to validate workspace layout and static assertions.
- Small-output-buffer deflate tests to exercise `flush_pending()` re-entry.
- Bit-exact tests around stored block alignment, partial flush alignment, and end-of-block emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_deflate/defutil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_dfltcc/Makefile -->
# sources/distributed-fs/ceph-client/lib/zlib_dfltcc/Makefile

Purpose: Builds the s390 DFLTCC zlib hardware acceleration object when `CONFIG_ZLIB_DFLTCC` is enabled.

Important entries:
- `obj-$(CONFIG_ZLIB_DFLTCC) += zlib_dfltcc.o`.
- `zlib_dfltcc-objs := dfltcc.o dfltcc_deflate.o dfltcc_inflate.o`.

Control flow: Kbuild links the common DFLTCC support plus deflate and inflate hook implementations into one object.

State and persistence: No runtime state; build configuration controls whether hook implementations are available to the zlib deflate/inflate objects.

Dependencies and integration:
- Integrates with `lib/zlib_deflate/deflate.c` and `lib/zlib_inflate/inflate.c` through `CONFIG_ZLIB_DFLTCC` include hooks.
- Architecture dependency is implicit: headers use s390 facility/setup and the DFLTCC instruction wrapper.

Risks:
- If enabled on an unsupported architecture, the architecture headers or inline assembly will fail; Kconfig must constrain selection.
- Partial object list changes can leave hooks unresolved.

Test signals:
- `CONFIG_ZLIB_DFLTCC=y/m` kernel build on s390.
- Build without the config to verify software zlib path remains independent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_dfltcc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc.c -->
# sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc.c

Purpose: Provides common state reset and diagnostic formatting for System z DEFLATE CONVERSION CALL acceleration.

Important APIs/functions:
- `oesc_msg()` converts a nonzero Operation-Ending-Supplemental Code into `strm->msg` text, except in static/pre-boot builds.
- `dfltcc_reset_state()` queries available hardware functions when DFLTCC is enabled, copies the query result into `dfltcc_state->af`, clears the parameter block, and initializes task flags.

Control flow:
- On reset, `is_dfltcc_enabled()` gates a `DFLTCC_QAF` query. If disabled, available-functions state is zeroed so callers fall back to software.
- The parameter block is then cleared and initialized with `nt = 1` and `ribm = DFLTCC_RIBM`.

State and persistence:
- Updates only `struct dfltcc_state` embedded in each zlib stream workspace.
- No global mutable state here; global support mode comes from `zlib_dfltcc_support` in s390 setup code.

Dependencies and integration:
- Includes `dfltcc_util.h` and `dfltcc.h`.
- Called by deflate and inflate reset hooks.
- Module metadata declares GPL license.

Risks:
- The QAF call temporarily uses the parameter block storage and then copies out the available-function query; ordering matters.
- `sprintf()` writes into a fixed 64-byte `msg` buffer with a fixed format. Safe for current format but should not be expanded carelessly.

Test signals:
- Boot/run with `zlib_dfltcc_support` disabled and enabled to verify QAF behavior and fallback.
- Force nonzero OESC paths to confirm `strm->msg` propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc.h -->
# sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc.h

Purpose: Defines DFLTCC constants, parameter block layouts, stream extension structures, state-placement macros, and the hardware-enabled predicate used by zlib DFLTCC glue.

Important APIs/types:
- `struct dfltcc_qaf_param` models Query Available Functions results.
- `struct dfltcc_param_v0` models the 1536-byte DFLTCC parameter block for GDHT/CMPR/XPND, including check value, history, block flags, dynamic Huffman table storage, and continuation state.
- `struct dfltcc_state` contains the common parameter block, available-function result, and message buffer.
- `struct dfltcc_deflate_state` extends common state with tuning thresholds and level masks.
- `GET_DFLTCC_STATE()` computes the aligned extension state immediately after inflate or deflate state.
- `is_dfltcc_enabled()` checks the command-line support mode and facility bit 151.

Control flow: Header-only predicates and layout definitions are used by reset and hook functions. `DEFLATE_DFLTCC_ENABLED()` maps to `is_dfltcc_enabled()`.

State and persistence:
- The DFLTCC parameter block persists across streaming calls and carries hardware continuation, history, checksum, and block state.
- `zlib_dfltcc_support` is an external s390 boot/setup control that can disable or restrict deflate/inflate acceleration.

Dependencies and integration:
- Includes `../zlib_deflate/defutil.h`, `<asm/facility.h>`, and `<asm/setup.h>`.
- Layout static assertions enforce hardware ABI size and alignment.
- Shared by DFLTCC deflate and inflate implementations.

Risks:
- Hardware ABI exactness is critical. Bitfield ordering, packing assumptions, offsets, and size must match s390 DFLTCC expectations.
- `GET_DFLTCC_STATE()` relies on the base zlib state being followed by aligned extension storage in the workspace.
- Facility probing must match the architecture; misuse outside s390 is invalid.

Test signals:
- Compile-time static assertions for parameter block size/offset.
- Runtime DFLTCC query on supported hardware.
- Cross-build tests with DFLTCC off to ensure the software path does not include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_deflate.c -->
# sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_deflate.c

Purpose: Implements the DFLTCC-backed deflate hook that can replace software block compression for supported s390 streams while preserving the zlib API and stream state semantics.

Important APIs/functions:
- `dfltcc_can_deflate()` checks command-line support mode, compression parameters, available hardware functions, and format support.
- `dfltcc_reset_deflate_state()` resets common hardware state and initializes level mask and block/DHT thresholds.
- `dfltcc_deflate()` is the hook called from `zlib_deflate()`.
- Internal `dfltcc_gdht()` asks hardware to generate a dynamic Huffman table sample.
- Internal `dfltcc_cmpr()` invokes `DFLTCC_CMPR | HBT_CIRCULAR` and updates stream pointers/counters.
- `send_eobs()` emits hardware-provided end-of-block bits through software bit helpers.

Control flow:
- If hardware cannot be used, the hook returns 0 and software deflate continues. On full flush while declining, it clears hardware history length.
- The hook manages open hardware blocks via `param->bcf`, buffered hardware output via `param->cf`, and dynamic-table renewal when thresholds are crossed.
- It masks excess input so each hardware block is bounded, avoids calling hardware with no output space, and may manually close blocks for non-NO_FLUSH modes.
- On starting a block, it chooses fixed Huffman for the initial small block threshold or generates a DHT for dynamic blocks.
- After CMPR, it maps parameter block fields back into zlib bit buffer/checksum state and sets the software `block_state` result.

State and persistence:
- Uses `struct dfltcc_deflate_state` adjacent to `deflate_state`. It persists hardware parameter block flags, checksum, history, thresholds, and availability.
- `strm->total_in`, `total_out`, `avail_in`, `avail_out`, `next_in`, and `next_out` are updated by hardware call wrappers.
- `state->bi_valid` and `state->bi_buf` bridge sub-byte hardware output with software block/trailer writers.

Dependencies and integration:
- Includes zlib deflate internals, `dfltcc_util.h`, `dfltcc_deflate.h`, s390 setup, and `<linux/zutil.h>`.
- Exported helper symbols allow other code/tests to inspect deflate hardware availability and reset behavior.
- Uses `zlib_tr_send_bits()` and `flush_pending()` from `defutil.h`.

Risks:
- Mixed hardware/software block closing is delicate: incorrect `bcf`, `bhf`, `sbb`, or pending buffer handling can corrupt the deflate bitstream.
- Hardware unsupported-parameter fallback must occur before any hardware output; after partial hardware use, some software fallbacks are impossible.
- Checksum ownership changes when DFLTCC is active, so Adler-32 correctness depends on `param->cv` mapping.
- Threshold and masking logic must ensure progress and avoid livelock with small inputs/output buffers.

Test signals:
- s390 DFLTCC compression tests at level 1, debug all-level mode, unsupported levels/strategies/window sizes, and command-line support modes.
- Flush-mode tests: NO_FLUSH, SYNC/FULL flush, FINISH with open block, and tiny output buffer.
- Verify output against software inflate and independent zlib.
- Test disabling DFLTCC mid-support only before hardware use; after use, ensure failure behavior is explicit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_deflate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_deflate.h -->
# sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_deflate.h

Purpose: Connects the generic deflate implementation to the s390 DFLTCC deflate hook through function declarations and preprocessor hook macros.

Important APIs/macros:
- Declares `dfltcc_can_deflate()`, `dfltcc_deflate()`, and `dfltcc_reset_deflate_state()`.
- `DEFLATE_RESET_HOOK(strm)` calls the DFLTCC reset function.
- `DEFLATE_HOOK` maps block compression to `dfltcc_deflate`.
- `DEFLATE_NEED_CHECKSUM(strm)` suppresses software checksum updates when hardware can deflate.

Control flow: Included by `deflate.c` when `CONFIG_ZLIB_DFLTCC` is set, replacing the no-op hook macros used by the software-only build.

State and persistence: No local state. It changes ownership of checksum and reset behavior for the stream when DFLTCC is available.

Dependencies and integration:
- Includes `dfltcc.h`.
- Bridges `deflate.c` to `dfltcc_deflate.c` without changing the generic compressor body.

Risks:
- Macro contracts must match `deflate.c` expectations exactly. `DEFLATE_HOOK` returns whether it handled the block and writes `block_state`.
- If `dfltcc_can_deflate()` changes semantics, checksum updates can be skipped incorrectly.

Test signals:
- Compile DFLTCC and non-DFLTCC builds.
- Runtime compare Adler/trailer output for hardware and software paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_deflate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_inflate.c -->
# sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_inflate.c

Purpose: Implements the DFLTCC-backed inflate hook for s390, allowing hardware expansion to run from the generic inflate state machine at block boundaries.

Important APIs/functions:
- `dfltcc_can_inflate()` checks command-line support mode and hardware XPND/FMT0 availability.
- `dfltcc_reset_inflate_state()` resets common DFLTCC state.
- `dfltcc_inflate()` performs the hardware expand operation or asks the generic inflate state machine to continue in software.
- Internal `dfltcc_inflate_disable()` disables future hardware use if still safe, or fails if hardware already emitted output and software cannot resume.
- Internal `dfltcc_xpnd()` wraps `DFLTCC_XPND | HBT_CIRCULAR` and updates stream pointers/availability.

Control flow:
- The generic `inflate.c` invokes this hook from `TYPEDO` before software block decoding.
- `Z_BLOCK` and `Z_PACKET_FLUSH` are unsupported by DFLTCC. If hardware has not been used, the hook disables availability and returns software fallback; otherwise it returns stream error.
- If the stream is at the last block, it moves to `CHECK`.
- For normal hardware inflate, the hook maps bit accumulator/checksum/history into the parameter block, loops while hardware reports AGAIN, maps output state back, and returns CONTINUE or BREAK based on operand exhaustion.
- Corrupt operand with OESC sets inflate mode BAD for generic error handling.

State and persistence:
- Uses the common `struct dfltcc_state` adjacent to `inflate_state`. `param->nt`, `param->cf`, `param->hl`, `param->sbb`, and `param->cv` preserve hardware continuation and checksum state.
- Hardware writes into the generic inflate sliding window, which must exist and be nonzero.

Dependencies and integration:
- Includes `../zlib_inflate/inflate.h`, `dfltcc_util.h`, `dfltcc_inflate.h`, s390 setup, and `<linux/zutil.h>`.
- Exported functions are available to module users/tests.

Risks:
- Once hardware has consumed data, software fallback may not have enough internal decode state to continue; this is explicitly guarded.
- The hook must preserve `state->bits`, `last`, `check`, and mode transitions exactly or the generic trailer/check path will misbehave.
- If no window is available, the code moves to `MEM`; workspace setup must keep the DFLTCC-aligned window valid.

Test signals:
- s390 inflate tests with DFLTCC enabled/disabled and deflate-only/inflate-only boot modes.
- Streams using `Z_BLOCK` and `Z_PACKET_FLUSH` before and after hardware use.
- Corrupt deflate streams with hardware OESC reporting.
- Tiny buffers and continuation-flag paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_inflate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_inflate.h -->
# sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_inflate.h

Purpose: Defines the generic inflate-to-DFLTCC hook interface and macros used by `inflate.c` when s390 hardware acceleration is enabled.

Important APIs/macros:
- Declares `dfltcc_reset_inflate_state()`, `dfltcc_can_inflate()`, and `dfltcc_inflate()`.
- Defines `dfltcc_inflate_action` with CONTINUE, BREAK, and SOFTWARE outcomes.
- `INFLATE_RESET_HOOK(strm)` resets DFLTCC state.
- `INFLATE_TYPEDO_HOOK(strm, flush)` calls hardware from `TYPEDO`, restoring/loading generic inflate locals around the call.
- `INFLATE_NEED_CHECKSUM(strm)` and `INFLATE_NEED_UPDATEWINDOW(strm)` suppress software checksum/window maintenance when hardware can inflate.

Control flow: The `INFLATE_TYPEDO_HOOK` macro can break the switch loop, jump to `inf_leave`, or let software continue based on the hook result.

State and persistence: No local state, but the macros change whether generic inflate updates `strm->adler` and the sliding window.

Dependencies and integration:
- Includes `dfltcc.h`.
- Tight integration with local variable names and labels in `inflate.c`: `RESTORE`, `LOAD`, `ret`, and `inf_leave`.

Risks:
- Macro coupling to `inflate.c` is fragile; renaming locals/labels or moving hook location breaks compilation or behavior.
- Skipping software window updates is safe only when DFLTCC history handling and window writes are correct.

Test signals:
- Build with DFLTCC enabled.
- Compare hardware and software inflate checksums/window behavior across chunked output buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_inflate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_util.h -->
# sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_util.h

Purpose: Provides the inline assembly wrapper for the s390 DFLTCC instruction plus utility helpers for bitset checks and parameter eligibility.

Important APIs/functions:
- `dfltcc()` wraps the `.insn rrf,0xb9390000` DFLTCC instruction using fixed registers r0-r5 and returns the condition code.
- `is_bit_set()` and `turn_bit_off()` inspect/edit QAF bitsets.
- `dfltcc_are_params_ok()` checks compression level mask, 32 KiB window, and default strategy.
- Declares `oesc_msg()`.

Control flow:
- `dfltcc()` copies pointer/length operands into register variables, runs inline assembly, then writes updated operands back to caller-provided pointers.
- After the instruction, it unpoisons parameter and output memory for KMSAN according to function type.
- The return value is the top two bits of the condition-code register captured by `ipm`.

State and persistence:
- No persistent local state. It mutates caller parameter blocks, stream pointers/lengths, and output memory.

Dependencies and integration:
- Includes `dfltcc.h`, `<linux/kmsan-checks.h>`, and `<linux/zutil.h>`.
- Used by query, dynamic table generation, compression, and expansion wrappers.

Risks:
- Register constraints and clobbers must match the architecture instruction ABI. Any compiler or inline-asm mistake can corrupt operands.
- KMSAN unpoison size calculations must match hardware writes, especially sub-byte compressed output.
- `dfltcc_are_params_ok()` limits hardware compression to known-safe zlib configurations; relaxing it requires hardware-format validation.

Test signals:
- s390 build and runtime hardware instruction smoke tests.
- KMSAN builds covering QAF/GDHT/CMPR/XPND paths.
- Parameter rejection tests for unsupported levels, strategies, and window sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_dfltcc/dfltcc_util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/Makefile -->
# sources/distributed-fs/ceph-client/lib/zlib_inflate/Makefile

Purpose: Kbuild recipe for the kernel zlib inflate module/object.

Important entries:
- `obj-$(CONFIG_ZLIB_INFLATE) += zlib_inflate.o`.
- `zlib_inflate-objs := inffast.o inflate.o infutil.o inftrees.o inflate_syms.o`.

Control flow: Build-time composition only. The object combines the state machine, fast decoder, table builder, utility blob helper, and symbol exports.

State and persistence: No runtime state.

Dependencies and integration:
- Selected by `CONFIG_ZLIB_INFLATE`.
- Used by boot decompressors, crypto, firmware, AppArmor, and other kernel decompression consumers.

Risks:
- Object list order must include symbol provider files. Omitting `inflate_syms.o` breaks modular users.
- Comments emphasize static allocation/no blocking allocation; callers still must provide per-stream workspace.

Test signals:
- Build with `CONFIG_ZLIB_INFLATE` built-in and modular if supported.
- Link checks for all exported inflate symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/inffast.c -->
# sources/distributed-fs/ceph-client/lib/zlib_inflate/inffast.c

Purpose: Fast-path DEFLATE decoder used by `inflate.c` when enough input and output space is available. It decodes literal/length and distance codes with reduced boundary checks and optimized match copying.

Important APIs/functions:
- `inflate_fast(z_streamp strm, unsigned start)` decodes from `state->mode == LEN` until input/output thresholds are reached, an end-of-block is found, or an error occurs.
- `get_unaligned16()` provides endian-independent 16-bit reads for architectures without efficient unaligned access.

Control flow:
- Copies stream and inflate state fields into locals for speed.
- Maintains `last = in + avail_in - 5` and `end = out + avail_out - 257`, relying on caller preconditions for safe inner-loop decoding.
- Reads at least 15 bits for literal/length lookup, follows second-level tables when needed, decodes extra length/distance bits, then copies literals or matches.
- Match copying handles three cases: back-reference into the sliding window, direct output copy with distance greater than 2, and short repeating distances 1 or 2 using 16-bit pattern replication.
- On end-of-block it sets mode `TYPE`; on invalid code or too-far distance it sets `BAD`.
- Restores unused bytes and updates `next_in`, `next_out`, `avail_in`, `avail_out`, `hold`, and `bits`.

State and persistence:
- Mutates `struct inflate_state` via `hold`, `bits`, and `mode`, but does not update checksums or the sliding window; `inflate.c` handles that on return.
- Reads fixed/dynamic decode tables from `state->lencode` and `state->distcode`.

Dependencies and integration:
- Includes zlib utility headers and `inftrees.h`, `inflate.h`, `inffast.h`.
- Called only by `inflate.c` when `have >= 6 && left >= 258`.
- Honors `CONFIG_HAVE_EFFICIENT_UNALIGNED_ACCESS` for 16-bit copy optimization.

Risks:
- Relies on strict entry preconditions. Calling with smaller buffers risks out-of-bounds reads/writes.
- Overlapping match copy logic is subtle, especially distances 1 and 2 and window wraparound.
- Availability restoration math is non-obvious and must stay consistent with sentinel `last`/`end`.

Test signals:
- Fuzzed inflate inputs with large buffers to maximize fast-path coverage.
- Back-reference tests for window wrap, distance 1/2, and distances crossing from window into output.
- Architecture tests with efficient and inefficient unaligned access settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/inffast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/inffast.h -->
# sources/distributed-fs/ceph-client/lib/zlib_inflate/inffast.h

Purpose: Internal declaration for the inflate fast decoder.

Important APIs:
- Declares `inflate_fast(z_streamp strm, unsigned start)`.

Control flow: No runtime logic. Included by `inflate.c` to call the optimized decode loop.

State and persistence: No state.

Dependencies and integration:
- Relies on zlib stream types already visible from including context.
- Not a public API; callers should use `<linux/zlib.h>`.

Risks:
- Signature must stay synchronized with `inffast.c` and `inflate.c` caller assumptions.

Test signals:
- Compile/link validation.
- Fast-path inflate coverage in `inflate.c` tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/inffast.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/inffixed.h -->
# sources/distributed-fs/ceph-client/lib/zlib_inflate/inffixed.h

Purpose: Provides precomputed fixed-Huffman decode tables for DEFLATE block type 1.

Important APIs/types:
- Defines `static const code lenfix[512]` and `static const code distfix[32]`.
- Entries use `struct code` from `inftrees.h`, with op/bits/val describing literals, lengths, distances, end-of-block, or invalid codes.

Control flow:
- Included inside `zlib_fixedtables()` in `inflate.c`. The include creates function-local static tables and assigns them to `state->lencode` and `state->distcode`.

State and persistence:
- Static read-only tables persist for the translation unit/function scope.
- No mutable state.

Dependencies and integration:
- Requires `code` to be defined before inclusion.
- Avoids rebuilding fixed Huffman tables at runtime.

Risks:
- Table contents must exactly match RFC1951 fixed-code definitions. Manual edits are high risk.
- Inclusion style is unusual; moving it to normal header scope changes linkage/visibility.

Test signals:
- Inflate streams containing fixed-Huffman blocks.
- Compare fixed-block decode with dynamic-table decode of equivalent data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/inffixed.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/inflate.c -->
# sources/distributed-fs/ceph-client/lib/zlib_inflate/inflate.c

Purpose: Implements kernel zlib inflate over a preallocated workspace. It parses zlib/raw deflate streams, builds decode tables, copies stored blocks, decodes compressed blocks through normal or fast paths, validates trailers, maintains the sliding window, and optionally delegates block processing to s390 DFLTCC.

Important APIs/functions:
- `zlib_inflate_workspacesize()` returns `sizeof(struct inflate_workspace)`.
- `zlib_inflateInit2()` initializes wrapper mode, window bits, state pointer, and workspace-backed window.
- `zlib_inflateReset()` resets counters, mode, checksum, code-table pointers, and window state.
- `zlib_inflate()` is the main streaming state machine.
- `zlib_inflateEnd()` validates stream teardown.
- `zlib_inflateIncomp()` adds incompressible bytes directly to output history/checksum.
- Internal `zlib_updatewindow()` maintains the circular 32 KiB window.
- Internal `zlib_fixedtables()` installs fixed Huffman tables from `inffixed.h`.
- Internal `zlib_inflateSyncPacket()` handles PPP packet flush semantics.

Control flow:
- `zlib_inflate()` loads stream fields into locals and loops over `state->mode`.
- Header handling validates zlib method/window/check and handles preset dictionary request via `Z_NEED_DICT`.
- `TYPEDO` invokes the DFLTCC hook if enabled, then reads the block type: stored, fixed, dynamic, or invalid.
- Stored blocks byte-align and copy length-checked data.
- Dynamic blocks parse code counts, build the code-length table, expand repeated lengths, then build literal/length and distance decode tables via `zlib_inflate_table()`.
- Literal/length decoding uses `inflate_fast()` when buffers are large enough; otherwise it decodes table entries step-by-step.
- Match copies read from either the output just produced or the sliding window; invalid distances set `BAD`.
- Trailer handling checks Adler-32 when wrapping is enabled, then returns `Z_STREAM_END`.
- All early exits go through `inf_leave` to restore state, update counters/checksum/window, and choose `Z_BUF_ERROR` on no progress or unfinished `Z_FINISH`.

State and persistence:
- Persistent state is `struct inflate_state` in the caller workspace plus `working_window` from `struct inflate_workspace`.
- Tracks parser mode, wrapper/checksum status, sliding window indexes, bit accumulator, current copy length/distance, decode table storage, and temporary code lengths.
- No dynamic allocation in normal inflate path.

Dependencies and integration:
- Includes `inftrees.h`, `inflate.h`, `inffast.h`, and `infutil.h`.
- DFLTCC macros from `../zlib_dfltcc/dfltcc_inflate.h` can override checksum/window behavior and block decoding.
- Exported through `inflate_syms.c`; `infutil.c` supplies a one-shot blob helper.

Risks:
- State machine fallthroughs are intentional and must be preserved.
- DFLTCC hook macros depend on local variables and labels.
- The code allows `next_out == NULL` for PowerPC zImage behavior, so generic null-output checks cannot be added blindly.
- Sliding window update is deferred; incorrect conditions can break future back-references.
- Dynamic table validation and distance checks are key corruption boundaries.

Test signals:
- Inflate raw and zlib-wrapped streams, stored/fixed/dynamic blocks, dictionaries, bad headers, bad checksums, invalid code lengths, invalid distances, and truncated input.
- Exercise small buffer streaming and large-buffer fast path.
- PPP `Z_PACKET_FLUSH` behavior through `zlib_inflateSyncPacket()`.
- s390 DFLTCC parity with software inflate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/inflate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/inflate.h -->
# sources/distributed-fs/ceph-client/lib/zlib_inflate/inflate.h

Purpose: Defines the internal inflate parser modes and `struct inflate_state` used by `inflate.c`, `inffast.c`, and DFLTCC inflate glue.

Important APIs/types:
- `inflate_mode` enumerates every parser/decode/trailer/error state: header modes, block type modes, stored/dynamic/code decode modes, check/done/error modes.
- `struct inflate_state` stores wrapper flags, checksum, sliding window, bit accumulator, copy/match state, decode table pointers, dynamic table counts, temporary lengths/workspace, and fixed-size code table storage.
- `REVERSE(q)` byte-swaps 32-bit checksum words from the bit accumulator.

Control flow: The mode enum documents state transitions consumed by the `inflate.c` switch loop. No executable code except macros.

State and persistence:
- This header defines the persistent state for a streaming inflate call. The state lives inside `struct inflate_workspace` in `infutil.h`.
- `codes[ENOUGH]`, `lens[320]`, and `work[288]` avoid allocation while building dynamic Huffman tables.

Dependencies and integration:
- Includes `inftrees.h` for `code` and `ENOUGH`.
- DFLTCC computes extension placement from this struct size/alignment.

Risks:
- Changing enum or struct fields must be coordinated with `inflate.c`, `inffast.c`, and DFLTCC hooks.
- Fixed array sizes are format-derived. Reducing them risks table overflow.

Test signals:
- Compile with all consumers.
- Inflate dynamic-block stress cases that approach `ENOUGH` and length-array limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/inflate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/inflate_syms.c -->
# sources/distributed-fs/ceph-client/lib/zlib_inflate/inflate_syms.c

Purpose: Exports the kernel inflate API symbols and declares module metadata.

Important APIs/functions:
- Exports `zlib_inflate_workspacesize`, `zlib_inflate`, `zlib_inflateInit2`, `zlib_inflateEnd`, `zlib_inflateReset`, `zlib_inflateIncomp`, and `zlib_inflate_blob`.
- Provides module description and GPL license.

Control flow: No runtime logic beyond symbol export metadata.

State and persistence: No local state. Exported symbols become available to in-kernel modular users.

Dependencies and integration:
- Includes `<linux/module.h>`, `<linux/init.h>`, and `<linux/zlib.h>`.
- Connects inflate implementation to crypto, firmware, boot helpers, and other subsystems.

Risks:
- Export ABI stability matters for modular consumers.
- `zlib_inflateIncomp` and `zlib_inflate_blob` are specialized helpers; removing exports can break less obvious users.

Test signals:
- Kernel/module link with `CONFIG_ZLIB_INFLATE`.
- `modpost` symbol validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/inflate_syms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/inftrees.c -->
# sources/distributed-fs/ceph-client/lib/zlib_inflate/inftrees.c

Purpose: Builds canonical Huffman decode tables for inflate from code-length arrays. It handles code-length tables, literal/length tables, and distance tables.

Important APIs/functions:
- `zlib_inflate_table(codetype type, unsigned short *lens, unsigned codes, code **table, unsigned *bits, unsigned short *work)` builds one decode table set.

Control flow:
- Counts code lengths, finds min/max length, clamps the requested root-table bits, and validates over-subscribed or incomplete code sets.
- Sorts symbols by code length into the caller-provided `work` array.
- Selects base/extra tables for CODES, LENS, or DISTS.
- Fills root table entries and allocates subtables when codes exceed root bits, tracking `used` against `ENOUGH`.
- Adds invalid-code markers for incomplete table slots and returns updated table pointer/root bits.

State and persistence:
- Stateless across calls. All storage is caller-provided via `table` and `work`.
- Uses static const base/extra arrays for length and distance symbols.

Dependencies and integration:
- Includes `<linux/zutil.h>` and `inftrees.h`.
- Called from `inflate.c` while parsing dynamic blocks.

Risks:
- Table construction is a core corruption boundary. Incorrect validation can accept malformed streams or overrun `state->codes`.
- `ENOUGH` is assumed sufficient; return `+1` signals insufficient table space.
- The backwards Huffman increment is format-specific and easy to break.

Test signals:
- Fuzz dynamic Huffman headers.
- Boundary tests for no symbols, single-symbol tables, incomplete/oversubscribed tables, max table usage, and invalid repeats from `inflate.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/inftrees.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/inftrees.h -->
# sources/distributed-fs/ceph-client/lib/zlib_inflate/inftrees.h

Purpose: Defines inflate decode table entries, table size constants, code-table type enum, and the `zlib_inflate_table()` prototype.

Important APIs/types:
- `typedef struct code { unsigned char op; unsigned char bits; unsigned short val; } code`.
- `ENOUGH` is the max dynamic table size reserved in `inflate_state`.
- `MAXD` reserves worst-case distance table space.
- `codetype` distinguishes CODES, LENS, and DISTS table generation.
- Declares `zlib_inflate_table()`.

Control flow: No executable logic. The comments define how `op`, `bits`, and `val` are interpreted by `inflate.c` and `inffast.c`.

State and persistence: No state. Constants influence `struct inflate_state` allocation.

Dependencies and integration:
- Used by `inflate.h`, `inflate.c`, `inffast.c`, `inffixed.h`, and `inftrees.c`.

Risks:
- `code` layout is assumed to be four bytes for compact decode tables.
- Changing op-bit encoding requires coordinated decoder changes.
- Reducing `ENOUGH` or `MAXD` can make valid streams fail.

Test signals:
- Static size/layout checks if added.
- Dynamic-Huffman inflate tests near maximum table usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/inftrees.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/infutil.c -->
# sources/distributed-fs/ceph-client/lib/zlib_inflate/infutil.c

Purpose: Provides `zlib_inflate_blob()`, a convenience helper to inflate a raw deflate blob into a caller-provided buffer using temporary stream/workspace allocation.

Important APIs/functions:
- `zlib_inflate_blob(void *gunzip_buf, unsigned int sz, const void *buf, unsigned int len)` returns decompressed byte count or negative errno-style errors.

Control flow:
- Allocates a `z_stream_s` and inflate workspace with `kmalloc`.
- Sets input/output pointers and calls `zlib_inflateInit2(strm, -MAX_WBITS)` because the gzip header is expected to be stripped.
- Calls `zlib_inflate(strm, Z_FINISH)` once and treats only `Z_STREAM_END` as success.
- Calls `zlib_inflateEnd()` then frees workspace and stream.

State and persistence:
- All state is temporary and freed before return.
- Does not persist decompressor state across calls.

Dependencies and integration:
- Includes `<linux/zutil.h>`, errno, slab, and vmalloc headers.
- Exported by `inflate_syms.c`.
- Useful for firmware/init data style one-shot raw deflate decompression.

Risks:
- Single-shot `Z_FINISH` requires provided input and output buffers to be complete and sized correctly.
- It returns `-EINVAL` for any zlib failure, losing detailed zlib error type.
- Comment says returns `Z_OK` if successful, but implementation returns decompressed length on success.

Test signals:
- One-shot raw deflate blob success, too-small output buffer, truncated input, malformed input, and allocation failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/infutil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/infutil.h -->
# sources/distributed-fs/ceph-client/lib/zlib_inflate/infutil.h

Purpose: Defines the inflate workspace wrapper and `WS(strm)` accessor used by the kernel static-allocation inflate implementation.

Important APIs/types:
- `struct inflate_workspace` contains `struct inflate_state inflate_state` and the backing `working_window`.
- With `CONFIG_ZLIB_DFLTCC`, it also includes `struct dfltcc_state` and over-allocates the window by one page for page alignment.
- `WS(strm)` casts `strm->workspace` to `struct inflate_workspace *`.

Control flow: No runtime logic except the accessor macro. `inflate.c` uses this to locate state/window from the caller-supplied workspace.

State and persistence:
- This is the full per-stream inflate persistent memory. Lifetime is controlled by the caller that owns `strm->workspace`.
- DFLTCC builds require `dfltcc_state` doubleword alignment, enforced by static assertion.

Dependencies and integration:
- Includes `<linux/zlib.h>`, and DFLTCC headers plus `<asm/page.h>` when configured.
- Used by `inflate.c` and workspace-size calculation.

Risks:
- Any struct layout change affects `zlib_inflate_workspacesize()` and DFLTCC `GET_DFLTCC_STATE()` assumptions.
- Callers must allocate at least `zlib_inflate_workspacesize()` bytes before `zlib_inflateInit2()`.

Test signals:
- Build with/without `CONFIG_ZLIB_DFLTCC`.
- Runtime allocation-size tests that initialize and reset streams repeatedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_inflate/infutil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/Makefile -->
# sources/distributed-fs/ceph-client/lib/zstd/Makefile

Purpose: Kbuild recipe for the in-kernel Zstandard compressor, decompressor, and common support objects.

Important entries:
- `obj-$(CONFIG_ZSTD_COMPRESS) += zstd_compress.o`.
- `obj-$(CONFIG_ZSTD_DECOMPRESS) += zstd_decompress.o`.
- `obj-$(CONFIG_ZSTD_COMMON) += zstd_common.o`.
- `zstd_compress-y` lists FSE/HUF and compressor strategy modules.
- `zstd_decompress-y` lists HUF and frame/block decompressor modules.
- `zstd_common-y` includes common debug, entropy, error, FSE decompression, and common API code.

Control flow: Build-time composition. The common object is shared by compressor/decompressor code and selected independently.

State and persistence: No runtime state. Kconfig controls which API surface is linked.

Dependencies and integration:
- Kernel consumers include crypto zstd, AppArmor rawdata compression, firmware decompression, initramfs/kernel image tools, and other zstd users through `<linux/zstd.h>`.

Risks:
- Missing common objects cause unresolved symbols for both compression and decompression.
- Updating upstream zstd files requires keeping the Makefile object split aligned with kernel module wrappers.

Test signals:
- Build all combinations of `CONFIG_ZSTD_COMMON`, `CONFIG_ZSTD_COMPRESS`, and `CONFIG_ZSTD_DECOMPRESS`.
- Link checks for exported zstd APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/allocations.h -->
# sources/distributed-fs/ceph-client/lib/zstd/common/allocations.h

Purpose: Supplies small inline allocation wrappers for zstd contexts, honoring optional `ZSTD_customMem` callbacks while defaulting to kernel zstd dependency allocation hooks.

Important APIs/functions:
- `ZSTD_customMalloc(size_t size, ZSTD_customMem customMem)`.
- `ZSTD_customCalloc(size_t size, ZSTD_customMem customMem)`.
- `ZSTD_customFree(void *ptr, ZSTD_customMem customMem)`.

Control flow:
- If a custom allocator exists, malloc/calloc route to it; calloc is emulated with allocation plus `ZSTD_memset`.
- Otherwise wrappers call `ZSTD_malloc`, `ZSTD_calloc`, and `ZSTD_free` from `zstd_deps.h`.
- Free ignores NULL and uses custom free when present.

State and persistence:
- No local state. Allocated memory lifetime is owned by the caller/context.

Dependencies and integration:
- Defines `ZSTD_DEPS_NEED_MALLOC`, includes `zstd_deps.h`, `compiler.h`, and `<linux/zstd.h>`.
- Used by zstd context/dictionary code that supports custom memory hooks.

Risks:
- In this kernel dependency layer, default `ZSTD_malloc`/`calloc` may be NULL stubs unless the build provides allocators; many kernel zstd paths use workspaces instead.
- If `customAlloc` is provided without compatible `customFree`, freeing can be wrong.
- Custom calloc does not check allocation failure before `ZSTD_memset`; current code calls `ZSTD_memset(ptr, 0, size)` unconditionally on custom allocation result.

Test signals:
- Custom allocator unit tests for malloc/calloc/free paths, including allocation failure.
- Workspace-only zstd paths should not rely on default heap allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/allocations.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/bits.h -->
# sources/distributed-fs/ceph-client/lib/zstd/common/bits.h

Purpose: Provides bit utility primitives for zstd/FSE/HUF code: count leading/trailing zeros, common-byte counts, high-bit lookup, and rotate-right operations.

Important APIs/functions:
- `ZSTD_countTrailingZeros32_fallback()`, `ZSTD_countTrailingZeros32()`.
- `ZSTD_countLeadingZeros32_fallback()`, `ZSTD_countLeadingZeros32()`.
- `ZSTD_countTrailingZeros64()`, `ZSTD_countLeadingZeros64()`.
- `ZSTD_NbCommonBytes(size_t val)`.
- `ZSTD_highbit32(U32 val)`.
- `ZSTD_rotateRight_U64/U32/U16()`.

Control flow:
- Uses compiler builtins for GCC-family builds where available; otherwise uses De Bruijn fallback tables for 32-bit cases.
- `ZSTD_NbCommonBytes()` chooses trailing-zero or leading-zero counting based on endianness and word size.
- Rotate helpers mask shift counts to generate compiler-friendly rotate patterns.

State and persistence:
- Stateless, aside from static const lookup tables inside fallback functions.

Dependencies and integration:
- Includes `mem.h` for `U32`, `U64`, `S32`, endian, and word-size helpers.
- Used by entropy parsing, match finding, and bitstream handling.

Risks:
- Functions assert nonzero inputs. Release builds may compile assertions out, so callers must guarantee nonzero values.
- Builtin behavior is undefined for zero; the assertion is not just documentation.
- Endianness-dependent common-byte logic must match the memory comparison algorithms that consume it.

Test signals:
- Unit tests for zero-excluded values, powers of two, high-bit boundaries, endian-specific common-byte behavior, and rotate counts.
- UBSAN tests for shift/count operations if enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/bitstream.h -->
# sources/distributed-fs/ceph-client/lib/zstd/common/bitstream.h

Purpose: Implements inline forward bitstream writing and reverse bitstream reading used by zstd entropy coders. Streams are LIFO: bits written first are read last.

Important APIs/types:
- `BIT_CStream_t` with bit container, bit position, and output pointers.
- `BIT_DStream_t` with bit container, consumed count, current pointer, start, and safe limit.
- `BIT_DStream_status` reports unfinished, end-of-buffer, completed, or overflow.
- Writer functions: `BIT_initCStream`, `BIT_addBits`, `BIT_addBitsFast`, `BIT_flushBits`, `BIT_flushBitsFast`, `BIT_closeCStream`.
- Reader functions: `BIT_initDStream`, `BIT_lookBits`, `BIT_lookBitsFast`, `BIT_readBits`, `BIT_readBitsFast`, `BIT_skipBits`, `BIT_reloadDStream`, `BIT_reloadDStreamFast`, `BIT_endOfDStream`.

Control flow:
- Writers accumulate bits into a machine-word container, flush full bytes to memory, and append a one-bit end mark on close.
- Readers initialize from the end of the byte buffer, locate the end mark in the last byte, then consume bits backward. Reload functions move the pointer toward the start while preserving safe reads near the buffer boundary.
- Safe reload detects overflow and end-of-buffer; fast reload assumes enough distance from the start.

State and persistence:
- State lives in caller-owned stream structs. No global state.
- Read/write pointers define the valid buffer region and must remain stable during operations.

Dependencies and integration:
- Includes `mem.h`, `compiler.h`, `debug.h`, `error_private.h`, and `bits.h`.
- Used by FSE and HUF compression/decompression paths.

Risks:
- Unsafe variants require clean values, nonzero bit counts, and valid buffer margins.
- `BIT_initDStream()` requires exact compressed bitstream size and a nonzero last byte end marker; malformed inputs return zstd errors.
- Pointer and shift arithmetic are performance-critical and easy to break on 32-bit vs 64-bit differences.

Test signals:
- Round-trip bitstream encode/decode on 32-bit and 64-bit builds.
- Boundary tests for 1-byte through word-sized streams, missing end mark, dst too small, overflow, and exact completion.
- Fuzz entropy streams consumed by FSE/HUF.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/bitstream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/compiler.h -->
# sources/distributed-fs/ceph-client/lib/zstd/common/compiler.h

Purpose: Centralizes compiler attributes, inlining macros, branch/prefetch hints, alignment helpers, fallthrough annotation, and sanitizer workarounds for kernel zstd code.

Important APIs/macros:
- Inline macros: `INLINE_KEYWORD`, `FORCE_INLINE_ATTR`, `FORCE_INLINE_TEMPLATE`, `HINT_INLINE`, `MEM_STATIC`, `FORCE_NOINLINE`.
- Target/prefetch macros: `TARGET_ATTRIBUTE`, `BMI2_TARGET_ATTRIBUTE`, `PREFETCH_L1`, `PREFETCH_L2`, `PREFETCH_AREA`.
- Optimization/control macros: `DONT_VECTORIZE`, `LIKELY`, `UNLIKELY`, `ZSTD_UNREACHABLE`, `ZSTD_FALLTHROUGH`.
- Alignment helpers: `ZSTD_isPower2`, `ZSTD_ALIGNOF`, `ZSTD_ALIGNED`.
- Pointer sanitizer helpers: `ZSTD_wrappedPtrDiff`, `ZSTD_wrappedPtrAdd`, `ZSTD_wrappedPtrSub`, `ZSTD_maybeNullPtrAdd`.

Control flow:
- Mostly preprocessor configuration based on compiler and target.
- Prefetch area loops over cache lines.
- Pointer helper functions isolate operations that intentionally rely on wrapping or NULL+0 behavior workarounds.

State and persistence: Stateless.

Dependencies and integration:
- Includes `<linux/types.h>` and `portability_macros.h`.
- Included across zstd common/compress/decompress code to keep upstream-like macros compatible with kernel builds.

Risks:
- Attribute and builtin checks must be accepted by the kernel compiler matrix.
- Pointer-overflow sanitizer exemptions are intentionally narrow; removing them can create false-positive UBSAN/ASAN reports in decompressor code.
- `ZSTD_FALLTHROUGH` maps to kernel `fallthrough`; include context must provide it.

Test signals:
- Build zstd under GCC and Clang, with sanitizers where supported.
- Cross-compile 32-bit, 64-bit, x86 BMI2-capable, and non-x86 targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/cpu.h -->
# sources/distributed-fs/ceph-client/lib/zstd/common/cpu.h

Purpose: Provides CPUID feature detection helpers used by zstd dynamic dispatch, especially BMI2 support checks on x86.

Important APIs/types:
- `ZSTD_cpuid_t` stores selected CPUID feature registers.
- `ZSTD_cpuid()` executes CPUID where supported and returns feature bits.
- Macro-generated predicates such as `ZSTD_cpuid_bmi1()`, `ZSTD_cpuid_bmi2()`, `ZSTD_cpuid_sse2()`, and many other x86 feature checks.

Control flow:
- On i386 PIC with GCC, preserves EBX around CPUID manually.
- On x86/x86_64, queries leaves 0, 1, and 7 when available.
- On non-x86, returns zeroed feature registers.

State and persistence:
- Stateless. Callers can cache `ZSTD_cpuid_t` if desired.

Dependencies and integration:
- Includes `mem.h` for `U32`.
- `zstd_internal.h` uses this to implement `ZSTD_cpuSupportsBmi2()`.

Risks:
- Inline assembly constraints must preserve ABI registers, especially 32-bit PIC EBX.
- CPUID only reports hardware support; OS support for wider vector state is not fully evaluated here.
- Non-x86 returns no features, which should force generic code paths.

Test signals:
- x86 and i386 PIC build/run tests.
- Verify BMI2 dispatch only on CPUs with both BMI1 and BMI2.
- Non-x86 build should compile and report no x86 features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/debug.c -->
# sources/distributed-fs/ceph-client/lib/zstd/common/debug.c

Purpose: Provides the optional global zstd debug verbosity variable when runtime debug logging is compiled in.

Important APIs/state:
- Defines `int g_debuglevel = DEBUGLEVEL` when `DEBUGLEVEL >= 2`.

Control flow: No functions. Conditional definition prevents an empty translation unit issue in non-kernel upstream contexts; in this kernel copy it only emits state for debug builds.

State and persistence:
- `g_debuglevel` is global mutable process/kernel state for zstd debug logging and is not thread-safe.

Dependencies and integration:
- Includes `debug.h`, whose `RAWLOG` and `DEBUGLOG` macros reference `g_debuglevel` when enabled.
- Built into `zstd_common.o`.

Risks:
- Runtime modification affects all zstd users globally.
- Debug logging at high levels can be very verbose and expensive.

Test signals:
- Build with default `DEBUGLEVEL=0` and with `DEBUGLEVEL>=2`.
- Confirm `DEBUGLOG` compiles and emits through kernel debug print hooks when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/debug.h -->
# sources/distributed-fs/ceph-client/lib/zstd/common/debug.h

Purpose: Defines zstd debug/assertion macros: compile-time assertions, optional runtime assertions, and optional debug/raw logging.

Important APIs/macros:
- `DEBUG_STATIC_ASSERT(c)` for compile-time checks inside functions.
- `DEBUGLEVEL` defaulting to 0.
- `assert(condition)` integration through `zstd_deps.h` when `DEBUGLEVEL >= 1`; otherwise disabled if not already defined.
- `RAWLOG(l, ...)` and `DEBUGLOG(l, ...)` when `DEBUGLEVEL >= 2`, backed by global `g_debuglevel`.

Control flow:
- Preprocessor selects no-op or active assertion/logging behavior.
- Active logging routes to `ZSTD_DEBUG_PRINT`, which the kernel dependency layer maps to `pr_debug`.

State and persistence:
- Header itself has no state; for debug level >=2 it declares external `g_debuglevel`.

Dependencies and integration:
- Includes `zstd_deps.h` only for enabled assert/logging support.
- Used throughout zstd/FSE/HUF code.

Risks:
- Assertions are compiled out at default level, so correctness cannot depend on them.
- Variadic logging macros must remain syntactically valid when disabled.
- High debug levels in kernel can be costly and noisy.

Test signals:
- Build with `DEBUGLEVEL=0`, `1`, and `2+`.
- Trigger a debug log path and verify `pr_debug` formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/entropy_common.c -->
# sources/distributed-fs/ceph-client/lib/zstd/common/entropy_common.c

Purpose: Implements shared FSE/HUF entropy helper functions used by zstd compression and decompression, primarily error wrappers and parsing compact normalized-count/Huffman-weight headers.

Important APIs/functions:
- `FSE_versionNumber()`.
- `FSE_isError()`, `FSE_getErrorName()`.
- `HUF_isError()`, `HUF_getErrorName()`.
- `FSE_readNCount()`, `FSE_readNCount_bmi2()`, and internal `FSE_readNCount_body()` parse normalized FSE counts from a compact bit header.
- `HUF_readStats()`, `HUF_readStats_wksp()`, and internal body functions parse Huffman weights and rank statistics, optionally using BMI2 paths.

Control flow:
- FSE count parsing reads tableLog, then iteratively decodes signed normalized counts and zero-run repeats from a little-endian bitstream, updating `remaining`, threshold, and symbol index until the distribution sums to one remaining slot.
- Short headers are copied into an 8-byte local buffer for the main parser.
- HUF stats parsing supports a direct nibble-packed header (`iSize >= 128`) or an FSE-compressed weights header. It then computes rank stats, infers the final symbol weight, validates power-of-two totals, and returns bytes consumed.
- BMI2-specific variants are compiled only under `DYNAMIC_BMI2`; otherwise flags are ignored.

State and persistence:
- Stateless across calls. Caller-provided arrays receive normalized counters, weights, rank stats, table log, and symbol counts.
- Uses stack workspace for the public `HUF_readStats()` wrapper.

Dependencies and integration:
- Includes `mem.h`, `error_private.h`, `fse.h`, `huf.h`, and `bits.h`.
- Calls `FSE_decompress_wksp_bmi2()` for compressed Huffman weight headers.
- Used by zstd block/header entropy decode paths.

Risks:
- This is a malformed-input boundary. Bounds checks on `hbSize`, `srcSize`, `maxSVPtr`, `hwSize`, and bit counts must remain exact.
- `ZSTD_highbit32()` requires nonzero inputs; the code validates totals before calling in most places.
- BMI2 dispatch must produce identical results to default path.

Test signals:
- Fuzz FSE normalized count headers and HUF stats headers.
- Boundary tests for tiny headers, too-small max symbol values, tableLog too large, too many zeros, invalid final weight, and workspace sizes.
- Compare BMI2 and non-BMI2 decoding results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/entropy_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/error_private.c -->
# sources/distributed-fs/ceph-client/lib/zstd/common/error_private.c

Purpose: Provides the central mapping from zstd internal error enum values to human-readable strings.

Important APIs/functions:
- `ERR_getErrorString(ERR_enum code)`.

Control flow:
- If `ZSTD_STRIP_ERROR_STRINGS` is defined, all codes return a stripped-message placeholder.
- Otherwise a switch maps stable and selected unstable `ZSTD_error_*` codes to string literals, with a default unspecified-code string.

State and persistence:
- No mutable state. Uses static const string pointer for the default not-error case.

Dependencies and integration:
- Includes `error_private.h`.
- Public wrappers in zstd/FSE/HUF use this through `ERR_getErrorName()` or `ZSTD_getErrorString()`.

Risks:
- Error enum changes in `<linux/zstd_errors.h>` must be reflected here, or callers get generic names.
- String stripping changes diagnostics but not error codes; tests should not require exact messages when stripped.

Test signals:
- Iterate all known error enum values and verify non-NULL strings.
- Build with and without `ZSTD_STRIP_ERROR_STRINGS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/error_private.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/error_private.h -->
# sources/distributed-fs/ceph-client/lib/zstd/common/error_private.h

Purpose: Defines internal zstd/FSE/HUF error-code encoding, propagation macros, and debug-aware return helpers.

Important APIs/macros:
- `ERR_enum` aliases `ZSTD_ErrorCode`; `PREFIX(name)` maps names to `ZSTD_error_*`.
- `ERROR(name)` and `ZSTD_ERROR(name)` encode errors as negative `size_t` values.
- `ERR_isError()`, `ERR_getErrorCode()`, and `ERR_getErrorName()` inspect encoded returns.
- `CHECK_V_F()` and `CHECK_F()` forward errors from called functions.
- `RETURN_ERROR_IF()`, `RETURN_ERROR()`, and `FORWARD_IF_ERROR()` return encoded errors and optionally log debug context.
- `_force_has_format_string()` and `_FORCE_HAS_FORMAT_STRING()` enforce valid variadic macro usage.
- Declares `ERR_getErrorString()`.

Control flow:
- Error-return macros check conditions or encoded return values and immediately return `size_t` error codes.
- Debug logging paths use `RAWLOG` with file/line and formatted context when enabled.

State and persistence:
- Stateless. Encoded error values are returned in `size_t`, a common zstd convention.

Dependencies and integration:
- Includes `<linux/zstd_errors.h>`, `compiler.h`, `debug.h`, and `zstd_deps.h`.
- Used throughout zstd common/compress/decompress code.

Risks:
- Error encoding assumes valid non-error sizes are never greater than `ERROR(maxCode)`. This convention must be preserved.
- Macros return from the current function, so they are appropriate only in functions returning `size_t` or compatible encoded errors.
- Debug formatting helpers must avoid evaluating arguments at runtime in disabled paths.

Test signals:
- Unit tests for `ERR_isError`, `ERR_getErrorCode`, and macro forwarding.
- Compile paths using empty and non-empty variadic macro arguments under strict C modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zstd/common/error_private.h -->
