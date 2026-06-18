# subset-b-006114 grouped research

Work item: subset-b-006114

This grouped report covers the requested Ceph-client Linux library sources. Each file section preserves its source path in the title and is wrapped with the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vsprintf.c -->
# sources/distributed-fs/ceph-client/lib/vsprintf.c

## Purpose
This file implements the Linux kernel's core string formatting and scanning routines: `vsnprintf`, `snprintf`, `scnprintf`, `sprintf`, binary printf support, and `vsscanf`/`sscanf`. It also owns kernel-specific printf extensions, especially the extended `%p` namespace used for symbols, resources, bitmaps, MAC/IP addresses, UUIDs, time values, device-tree nodes, flags, dentries, files, block devices, clocks, escaped buffers, and pointer security policies.

## Important APIs, types, and functions
Public exports include the legacy numeric parsers `simple_strtoull`, `simple_strtoul`, `simple_strntoul`, `simple_strtol`, `simple_strtoll`; formatting APIs `num_to_str`, `vsnprintf`, `vscnprintf`, `snprintf`, `scnprintf`, `vsprintf`, `sprintf`; optional `vbin_printf` and `bstr_printf` under `CONFIG_BINARY_PRINTF`; and scanning APIs `vsscanf` and `sscanf`. Internal core types are `struct printf_spec`, which captures flags/base/precision/width, `struct fmt`, which carries parser state, and `enum format_state`, which drives the formatter state machine.

Key helpers include `number` for integer formatting, decimal emitters based on `put_dec`, `format_decode` for parsing a format token, `pointer` for dispatching extended `%p` handlers, `check_pointer` for null/low/error pointer handling, and many specialized printers such as `resource_string`, `bitmap_string`, `ip_addr_string`, `escaped_string`, `uuid_string`, `time_and_date`, `flags_string`, `device_node_string`, and `fwnode_string`.

## Control flow
`vsnprintf` iterates through the format string by repeatedly calling `format_decode`. Literal spans are copied directly. Numeric, width, precision, char, string, pointer, and percent states each consume the corresponding `va_list` value and delegate to helpers. Unsupported tokens trigger `FORMAT_STATE_INVALID`, stop further argument consumption, and warn. Pointer formats are parsed after `%p` by `pointer`, which switches on the suffix and advances over alphanumeric suffix bytes in the caller.

`vbin_printf` parses the same format stream but serializes the argument values into a 32-bit word buffer; pointer formats that dereference data are resolved immediately into strings. `bstr_printf` replays those binary arguments back through the normal formatting logic. `vsscanf` is a separate scanner state machine supporting whitespace matching, literal matching, assignment suppression, field widths, integer bases, qualifiers, `%c`, `%s`, a constrained `%[...]`, `%n`, and `%%`.

## State and persistence behavior
Most formatting is stateless per call, but pointer formatting has global boot/runtime state. `no_hash_pointers`, `hash_pointers_mode`, and `kptr_restrict` control address disclosure. `ptr_key` and `filled_random_ptr_key` hold the SipHash key initialized through `execute_with_initialized_rng`; memory barriers pair the key write with later readers. `debug_boot_weak_hash` allows early boot hashed pointer output before strong random seeding. No persistent storage is used; state is in kernel globals and boot parameters.

## Dependencies and integration points
The file depends heavily on kernel core headers and subsystems: kallsyms, credentials/capabilities, RCU, dcache/files, block devices, resources, net address helpers, RTC/time, UUID helpers, firmware/device-tree property APIs, clocks, string escaping, SipHash/random, unaligned access, and trace flag name tables from `../mm/internal.h`. It is an integration hub for printk, procfs/sysfs format generation, tracing, binary printk, and many diagnostics.

## Risks
The primary risks are security and varargs correctness. `%p` defaults must not leak kernel addresses unless explicitly configured; `%pK` must not be used from IRQ/NMI context with credential checks; early random-key unavailability prints placeholders. Any mismatch between `format_decode` and argument consumption can desynchronize `va_list` use. Buffer sizing is designed around C99 `vsnprintf` semantics, but callers of `sprintf`/`vsprintf` can still overflow their destination. Pointer extension handlers must avoid recursive printk or complex fault-prone behavior in error paths. `vsscanf` intentionally differs from glibc for scansets and has limited assignment suppression behavior.

## Test signals
Strong signals are kernel printf format selftests, printk-format documentation conformance, kallsyms and `%p` address-hashing tests, binary printk round trips, `sscanf` parser tests, build coverage with and without `CONFIG_BINARY_PRINTF`, `CONFIG_KALLSYMS`, `CONFIG_BLOCK`, `CONFIG_OF`, `CONFIG_COMMON_CLK`, and runtime checks for boot parameters `hash_pointers`, `no_hash_pointers`, and `debug_boot_weak_hash`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/vsprintf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/win_minmax.c -->
# sources/distributed-fs/ceph-client/lib/win_minmax.c

## Purpose
This file implements a constant-space, constant-time windowed minimum/maximum tracker based on Kathleen Nichols' algorithm. It tracks the best, second-best, and third-best samples over a moving time window, approximating an exact window scan without storing every sample. Typical users track metrics such as minimum RTT over recent time.

## Important APIs, types, and functions
The exported APIs are `minmax_running_max` and `minmax_running_min`. They operate on `struct minmax`, which stores three `struct minmax_sample` values with timestamp `t` and value `v`. The internal helper `minmax_subwin_update` ages the three candidates as time advances. `minmax_reset`, defined in the public header, is used to replace all candidates when a new best value arrives or the window is empty.

## Control flow
Each update builds a `val` sample from `(t, meas)`. For maximum tracking, a measurement greater than or equal to the current best resets all candidates; for minimum tracking, a measurement less than or equal to the current best does the same. If the third candidate is older than the window, the tracker also resets because no useful sample remains. Otherwise, the new sample may replace the second or third candidate. `minmax_subwin_update` then promotes candidates if the best is out of the full window, or seeds the second and third choices after one-quarter and one-half window intervals.

## State and persistence behavior
State is entirely caller-owned in `struct minmax`; the file has no global mutable data and no persistence. Timestamp arithmetic uses unsigned `u32` subtraction, so callers are expected to provide monotonic wrapping time values in the same units as `win`.

## Dependencies and integration points
The code depends on `linux/win_minmax.h` for data structures and `minmax_reset`, and on module export infrastructure. It integrates with kernel networking and scheduling style metrics that need cheap moving-window extrema.

## Risks
The tracker is approximate by design, so monotonically changing streams can have bounded error. Wrong units or non-monotonic timestamps degrade the window semantics. Very small `win` values can make quarter/half-window promotion less meaningful. The implementation is not internally synchronized; callers must serialize access to a shared `struct minmax`.

## Test signals
Useful tests feed monotonic increasing, monotonic decreasing, flat, and bursty streams and compare the approximate result against an exact sliding-window implementation. Wraparound timestamp tests are important because unsigned subtraction is part of the design. Concurrency tests belong at caller sites, not inside this stateless helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/win_minmax.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xarray.c -->
# sources/distributed-fs/ceph-client/lib/xarray.c

## Purpose
This file implements the Linux XArray data structure: an RCU-readable, lock-protected radix-tree-like indexed pointer store with marks, allocation tracking, retry entries, value entries, optional multi-index entries, and iteration helpers. It is the modern replacement for many radix tree uses in memory management, ID allocation, page cache style storage, and subsystem object indexes.

## Important APIs, types, and functions
Advanced state APIs include `xas_load`, `xas_nomem`, `xas_create_range`, `xas_store`, mark operations, split helpers under `CONFIG_XARRAY_MULTI`, iteration helpers `xas_find`, `xas_find_marked`, conflict detection, and `xas_pause`. Public convenience APIs include `xa_load`, `xa_store`, `__xa_store`, `xa_erase`, `__xa_erase`, `__xa_cmpxchg`, `__xa_insert`, `xa_store_range`, `xa_get_order`, `__xa_alloc`, `__xa_alloc_cyclic`, mark getters/setters/clearers, `xa_find`, `xa_find_after`, `xa_extract`, `xa_delete_node`, and `xa_destroy`.

Core structures are declared in `linux/xarray.h`: `struct xarray`, `struct xa_state`, and `struct xa_node`. This file manipulates node slots, marks, parent links, counts, value counts, sibling entries, retry entries, and lock modes.

## Control flow
Lookup starts at `xas_start`, descends through `xas_descend`, and returns either a leaf entry, an internal retry/sibling state, or bounds/error. Stores use `xas_create` and `xas_expand` to allocate enough height, then `xas_store` replaces slots, frees detached subtrees with retry markers for RCU walkers, updates node counts and value counts, initializes or squashes marks, and shrinks/deletes empty nodes. Allocation APIs search `XA_FREE_MARK`, store the requested entry, clear the free mark, and optionally wrap cyclic IDs.

Iteration moves with `__xas_next`, `__xas_prev`, `xas_find`, or `xas_find_marked`, using node offsets and mark bitmaps to skip empty or unmarked regions. Multi-index support stores a canonical entry plus sibling entries, can split large entries into smaller ranges, and preserves marks across split boundaries.

## State and persistence behavior
All persistent state lives in caller-owned `struct xarray` nodes allocated from `radix_tree_node_cachep`. Readers use RCU; writers hold the selected xarray lock variant. Freed nodes are retired through `call_rcu` or direct cleanup of preallocated nodes in an `xa_state`. Mark state is aggregated from leaves up to root flags. Allocation mode uses `XA_FREE_MARK`, `XA_ZERO_ENTRY`, and `XA_FLAGS_ALLOC_WRAPPED` to persist free-slot and cyclic-wrap state.

## Dependencies and integration points
The implementation depends on bitmap helpers, RCU, slab/LRU allocation, export infrastructure, `linux/xarray.h`, and radix-tree internals for node allocation/freeing. `xa_delete_node` is a private integration point for workingset code and tests. Debug dumping uses printk when `XA_DEBUG` is enabled.

## Risks
Correctness risks center on RCU lifetime, sibling entries, mark propagation, and error-state handling. Storing advanced/internal entries through public APIs is rejected because it would corrupt invariants. Callers must obey locking rules: low-level `__xa_*` APIs require `xa_lock`, while read APIs may return stale values under RCU. Multi-index operations can be subtle around range alignment, split allocation, and conflict checks. Memory allocation may drop and reacquire locks in `__xas_nomem`, so callers must tolerate retries.

## Test signals
The nearby `test_xarray.c` is the main unit signal. Important coverage includes single and multi-index stores, erases, node shrink/expand, mark set/clear/find, allocation and cyclic allocation boundaries, retry entries under RCU, range stores, split helpers, `xa_extract`, and debug builds with `XA_NODE_BUG_ON` checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xarray.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xxhash.c -->
# sources/distributed-fs/ceph-client/lib/xxhash.c

## Purpose
This file provides the kernel implementation of xxHash 32-bit and 64-bit non-cryptographic hashing. It supports one-shot `xxh32`/`xxh64` hashing and streaming 64-bit hashing through `xxh64_state`. The algorithm is optimized for speed and stable output, not for adversarial collision resistance.

## Important APIs, types, and functions
Exports include `xxh32`, `xxh64`, `xxh64_reset`, `xxh64_update`, and `xxh64_digest`. Internal helpers are `xxh32_round`, `xxh64_round`, `xxh64_merge_round`, and rotate macros. Constants `PRIME32_*` and `PRIME64_*` define the xxHash mixing primes. The streaming state tracks total length, partial buffered bytes, and four accumulators.

## Control flow
The one-shot hash functions process large aligned logical lanes using unaligned little-endian loads, then process remaining 8-, 4-, and 1-byte tails, and finish with avalanche mixing. `xxh64_reset` initializes accumulators from the seed. `xxh64_update` buffers input until it can process 32-byte stripes, then updates accumulators in a loop and preserves tail bytes. `xxh64_digest` folds either the four accumulators or the short-input seed path, accounts for total length, processes buffered tail bytes, and avalanches the result.

## State and persistence behavior
One-shot functions are stateless. Streaming state is fully caller-owned in `struct xxh64_state`; there is no global mutable state. `xxh64_update` returns `-EINVAL` for null input and otherwise mutates the state incrementally.

## Dependencies and integration points
The file depends on kernel unaligned little-endian accessors, errno, compiler/kernel types, string helpers, module exports, and `linux/xxhash.h`. It is suitable for checksums, hash tables, deduplication hints, and compression/filesystem code that needs fast deterministic hashes.

## Risks
xxHash is not cryptographic and must not be used for authentication, secrets, or collision-resistant identifiers. The implementation assumes the caller supplies valid memory for the given length. Endianness is normalized through little-endian unaligned loads, preserving cross-platform results. Streaming users must call `xxh64_reset` before updates and must not share a mutable state concurrently without external synchronization.

## Test signals
Known upstream xxHash vectors should validate `xxh32`, `xxh64`, short inputs, long inputs, seeds, and streaming updates split at many boundaries. Cross-endian and unaligned-input tests are important integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xxhash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/Kconfig -->
# sources/distributed-fs/ceph-client/lib/xz/Kconfig

## Purpose
This Kconfig file defines kernel configuration switches for the in-kernel XZ decompressor, optional branch/call/jump filters, MicroLZMA support, and the decoder test module.

## Important options
`XZ_DEC` is the tristate main decompression support and selects `CRC32`. Per-architecture BCJ filter options include `XZ_DEC_X86`, `XZ_DEC_POWERPC`, `XZ_DEC_ARM`, `XZ_DEC_ARMTHUMB`, `XZ_DEC_ARM64`, `XZ_DEC_SPARC`, and `XZ_DEC_RISCV`; each defaults to yes under `XZ_DEC` and selects the hidden `XZ_DEC_BCJ`. `XZ_DEC_MICROLZMA` enables the compact MicroLZMA header variant. `XZ_DEC_TEST` builds a character-device tester and depends on `XZ_DEC`.

## Control flow
The file gates filter choices inside `if XZ_DEC`, so BCJ and MicroLZMA options are only visible when the decompressor is enabled. `XZ_DEC_BCJ` is hidden and selected indirectly by architecture filter choices. `XZ_DEC_TEST` is outside the main conditional but depends on the decompressor.

## State and persistence behavior
Kconfig choices persist in the kernel configuration and drive preprocessor symbols consumed by `xz_private.h`, `Makefile`, and the decoder sources. There is no runtime state in this file.

## Dependencies and integration points
The main integration is with `lib/xz/Makefile`, which builds `xz_dec.o` and optionally `xz_dec_bcj.o` and `xz_dec_test.o`. The selected config symbols map to `XZ_DEC_*` macros in `xz_private.h`.

## Risks
Disabling a BCJ filter can make valid `.xz` streams using that filter fail with `XZ_OPTIONS_ERROR`. Enabling `XZ_DEC_TEST` exposes a diagnostic character device and should remain off outside decoder development. MicroLZMA should only be enabled for consumers such as EROFS that need it.

## Test signals
Configuration matrix builds should cover `XZ_DEC=m/y`, each BCJ option toggled under expert configs, `XZ_DEC_MICROLZMA`, and `XZ_DEC_TEST=m`. Runtime tests should decode streams with each enabled filter and verify unsupported filters fail cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/Makefile -->
# sources/distributed-fs/ceph-client/lib/xz/Makefile

## Purpose
This Makefile wires the in-kernel XZ decoder objects to Kconfig selections.

## Important build targets
`obj-$(CONFIG_XZ_DEC) += xz_dec.o` builds the main decoder composite object. `xz_dec-y` includes `xz_dec_syms.o`, `xz_dec_stream.o`, and `xz_dec_lzma2.o`. `xz_dec-$(CONFIG_XZ_DEC_BCJ)` conditionally adds `xz_dec_bcj.o`. `obj-$(CONFIG_XZ_DEC_TEST) += xz_dec_test.o` builds the optional tester module.

## Control flow
Kbuild composes `xz_dec.o` from unconditional stream/LZMA2/symbol pieces and conditionally includes BCJ support. The test module is separate and only built when requested.

## State and persistence behavior
There is no runtime state. The file persists build graph decisions derived from `.config`.

## Dependencies and integration points
This integrates with the `lib/xz/Kconfig` symbols and the kernel module/export mechanism in `xz_dec_syms.c`. Consumers include in-kernel decompression users that link against exported XZ APIs.

## Risks
If `xz_dec_bcj.o` is omitted while streams require BCJ filters, the decoder will reject those streams. The Makefile assumes the common object name `xz_dec.o`; downstream build changes must preserve the composite object layout or exports may disappear.

## Test signals
Build tests should verify object inclusion for `CONFIG_XZ_DEC=y/m`, `CONFIG_XZ_DEC_BCJ=y`, and `CONFIG_XZ_DEC_TEST=m`. Link tests should confirm exported symbols resolve for module consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_crc32.c -->
# sources/distributed-fs/ceph-client/lib/xz/xz_crc32.c

## Purpose
This file implements the compact internal CRC32 routine used by the XZ decoder in environments that do not use the kernel `crc32_le` helper, such as preboot decompression.

## Important APIs, types, and functions
`xz_crc32_init` fills `xz_crc32_table[256]` using the IEEE 802.3 reflected polynomial `0xEDB88320`. `xz_crc32` updates a CRC over a byte buffer using the table. `STATIC_RW_DATA` allows architecture-specific preboot placement of mutable static data.

## Control flow
Initialization iterates over all byte values and folds each through eight polynomial steps. The update function bitwise complements the incoming CRC, table-folds each byte, then complements the result on return.

## State and persistence behavior
The only mutable state is `xz_crc32_table`. It must be initialized before use when this implementation is compiled in. There is no dynamic allocation.

## Dependencies and integration points
The file includes `xz_private.h`; `xz_stream.h` may instead map `xz_crc32` to kernel `crc32_le` when `__KERNEL__` and not `XZ_INTERNAL_CRC32`. It is used by stream header, block, index, footer, and optional check validation.

## Risks
Forgetting `xz_crc32_init` in preboot/internal builds breaks all CRC validation. This compact implementation trades speed for size and is not a hardware-accelerated CRC path.

## Test signals
Known CRC32 vectors, XZ header/footer CRC validation, and full `.xz` decode tests with CRC32 checks are the important signals. Preboot builds should verify table initialization order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_crc32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_dec_bcj.c -->
# sources/distributed-fs/ceph-client/lib/xz/xz_dec_bcj.c

## Purpose
This file implements XZ Branch/Call/Jump filter decoders. BCJ filters post-process LZMA2 output for executable code by converting relative branch targets back to their original form. Supported filters are compiled conditionally for x86, PowerPC, ARM, ARM-Thumb, SPARC, ARM64, and RISC-V.

## Important APIs, types, and functions
The private state `struct xz_dec_bcj` tracks filter type, downstream return value, single-call mode, absolute output position, x86 mask state, output-buffer scratch values, and a 16-byte temp buffer. Public internal APIs are `xz_dec_bcj_create`, `xz_dec_bcj_reset`, and `xz_dec_bcj_run`. Architecture helpers include `bcj_x86`, `bcj_powerpc`, `bcj_arm`, `bcj_armthumb`, `bcj_sparc`, `bcj_arm64`, and `bcj_riscv`; `bcj_apply` dispatches without function pointers.

## Control flow
`xz_dec_bcj_reset` validates the filter ID against compiled-in support, clears position and temp state, and sets the active type. `xz_dec_bcj_run` wraps `xz_dec_lzma2_run`: it first flushes already-filtered temp bytes, decodes more LZMA2 output into the caller buffer or temp buffer, applies the selected BCJ transform to bytes that are safe to process, stores unfilterable lookahead bytes in temp, and returns `XZ_OK` or `XZ_STREAM_END` according to downstream progress.

## State and persistence behavior
BCJ state persists across streaming calls because instruction windows can cross output-buffer boundaries. `pos` tracks the absolute block position, `x86_prev_mask` preserves x86 call-mask context, and `temp` stores a mix of filtered and unfiltered lookahead bytes. State is per decoder instance and freed through `kfree` via `xz_dec_bcj_end`.

## Dependencies and integration points
The file depends on `xz_private.h`, unaligned endian helpers, and the LZMA2 decoder. `xz_dec_stream.c` activates it when a Block Header contains a two-filter chain with a BCJ filter followed by LZMA2. Kconfig controls which filter IDs are accepted.

## Risks
Boundary handling is the main risk: each architecture has alignment and lookahead requirements, and mishandling temp bytes corrupts output. Unsupported filter IDs must return `XZ_OPTIONS_ERROR`. BCJ uses output bytes as workspace in single-call mode, so unsuccessful single-call decode must be rolled back by the stream wrapper.

## Test signals
Use `.xz` streams compressed with every enabled BCJ filter, small output buffers to force temp buffering, single-call and multi-call modes, and unsupported-filter fixtures. Architecture-specific exact-size and boundary tests are especially valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_dec_bcj.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_dec_lzma2.c -->
# sources/distributed-fs/ceph-client/lib/xz/xz_dec_lzma2.c

## Purpose
This file implements raw LZMA2 decompression and optional MicroLZMA decoding for the kernel XZ decoder. It handles dictionary management, range decoding, LZMA probability models, LZMA2 chunk control bytes, allocation modes, and output flushing.

## Important APIs, types, and functions
Internal public APIs are `xz_dec_lzma2_create`, `xz_dec_lzma2_reset`, `xz_dec_lzma2_run`, and `xz_dec_lzma2_end`. With `CONFIG_XZ_DEC_MICROLZMA`, it also provides `xz_dec_microlzma_alloc`, `xz_dec_microlzma_reset`, `xz_dec_microlzma_run`, and `xz_dec_microlzma_end`.

Important state structures are `struct dictionary`, `struct rc_dec`, `struct lzma_len_dec`, `struct lzma_dec`, `struct lzma2_dec`, and `struct xz_dec_lzma2`. Key helpers include dictionary reset/limit/get/put/repeat/copy/flush, range decoder operations `rc_read_init`, `rc_bit`, `rc_bittree`, `rc_direct`, LZMA symbol decoders `lzma_literal`, `lzma_match`, `lzma_rep_match`, and chunk wrapper `lzma2_lzma`.

## Control flow
`xz_dec_lzma2_reset` decodes dictionary-size properties, enforces memory limits, allocates or reuses the dictionary, and initializes the LZMA2 control state. `xz_dec_lzma2_run` then loops through the LZMA2 sequence states: control byte, uncompressed size, compressed size, optional new LZMA properties, range-coder preparation, LZMA run, or uncompressed copy. LZMA chunks set dictionary/output limits, call `lzma2_lzma`, flush dictionary bytes, and validate compressed size, pending match length, and range-coder finished state at chunk end.

`lzma_main` decodes literals and matches while there is dictionary space and enough input. Match distances are validated by `dict_repeat`, preventing reads before the beginning of the stream or beyond dictionary size. `lzma2_lzma` protects the core decoder's assumption that it can safely read up to `LZMA_IN_REQUIRED` bytes by staging boundary input in `temp.buf`.

## State and persistence behavior
Decoder state is per instance. In `XZ_SINGLE`, the dictionary points directly into the caller output buffer. In `XZ_PREALLOC`, dictionary memory is allocated once at `dict_max`. In `XZ_DYNALLOC`, dictionary memory grows with stream requirements up to the limit. Probability arrays, recent match distances, range coder state, chunk counters, temp input, and dictionary positions persist across multi-call invocations.

## Dependencies and integration points
The file depends on `xz_private.h`, `xz_lzma2.h`, `vmalloc`/`vfree`, and kernel allocation helpers. It is called directly by `xz_dec_stream.c`, or through `xz_dec_bcj.c` when a BCJ filter is active. MicroLZMA provides a separate public API for consumers that use that compact format.

## Risks
Risks include dictionary limit mistakes, malformed chunk-control handling, range-coder boundary reads, integer limit assumptions around compressed/uncompressed counters, and memory pressure for large dictionaries. The code caps normal LZMA2 dictionary properties to 3 GiB and reports `XZ_MEMLIMIT_ERROR` or `XZ_MEM_ERROR` when allocation constraints fail. Single-call mode intentionally rolls back at a higher layer if decoding fails.

## Test signals
Test vectors should cover uncompressed chunks, compressed chunks with every control-byte class, property resets, dictionary resets, maximum match lengths, invalid distances, truncated range-coder input, tiny output buffers, all allocation modes, memory-limit failures, and MicroLZMA exact/non-exact uncompressed-size behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_dec_lzma2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_dec_stream.c -->
# sources/distributed-fs/ceph-client/lib/xz/xz_dec_stream.c

## Purpose
This file implements the `.xz` container stream decoder. It validates stream headers and footers, parses block headers, wires the filter chain, checks compressed and uncompressed sizes, validates CRC32 and Index records, and exposes the main `xz_dec_*` API used by kernel consumers.

## Important APIs, types, and functions
Public APIs are `xz_dec_init`, `xz_dec_reset`, `xz_dec_run`, and `xz_dec_end`. Main state is `struct xz_dec`, which tracks the high-level sequence, VLI parsing state, CRC, check type, mode, block metadata, block hash, index hash, temp header buffer, LZMA2 decoder, and optional BCJ decoder. Helpers include `fill_temp`, `dec_vli`, `dec_block`, `index_update`, `dec_index`, `crc32_validate`, `check_skip`, `dec_stream_header`, `dec_stream_footer`, `dec_block_header`, and `dec_main`.

## Control flow
`xz_dec_run` wraps `dec_main` and applies single-call versus multi-call progress semantics. `dec_main` is a state machine: read Stream Header, read each Block Header, decode Block data through LZMA2 or BCJ+LZMA2, consume block padding, validate check bytes, parse Index, validate Index padding and CRC32, then validate Stream Footer. Header and footer data are accumulated in `temp` to simplify partial-input handling.

Block Header parsing validates CRC32, rejects unsupported flags, decodes optional compressed/uncompressed sizes, optionally resets a BCJ filter, requires LZMA2 filter ID `0x21` with one property byte, resets LZMA2, and verifies padding. Index parsing validates record count and hashes unpadded/uncompressed sizes to compare against block-observed hashes.

## State and persistence behavior
`struct xz_dec` persists all stream, block, index, CRC, and temp-buffer state across multi-call invocations. `allow_buf_error` implements the two-consecutive-no-progress rule for returning `XZ_BUF_ERROR`. `xz_dec_reset` returns a decoder to Stream Header state without freeing allocations. `xz_dec_end` frees LZMA2, optional BCJ, and top-level state.

## Dependencies and integration points
The file depends on `xz_private.h`, `xz_stream.h`, the LZMA2 decoder, optional BCJ decoder, CRC32 support, and kernel allocation. `xz_dec_syms.c` exports these APIs for modules. It is the central integration point for in-kernel `.xz` consumers.

## Risks
Container parsing must reject non-minimal VLIs, invalid CRCs, unsupported check types, unsupported filter chains, malformed padding, block size mismatches, and index/footer inconsistencies. Single-call mode uses output as workspace for some filter chains, so failed decodes must reset input/output positions. Multi-call callers must respond correctly to `XZ_OK`, `XZ_STREAM_END`, and `XZ_BUF_ERROR`.

## Test signals
Important signals are valid `.xz` files with no check and CRC32 check, multiple blocks, block sizes present/absent, BCJ filter chains, unsupported checks, unsupported filters, corrupt headers/footers/indexes, non-minimal VLIs, truncated streams, and small incremental input/output buffers that exercise every sequence transition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_dec_stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_dec_syms.c -->
# sources/distributed-fs/ceph-client/lib/xz/xz_dec_syms.c

## Purpose
This file provides module exports and module metadata for the XZ decompressor.

## Important APIs, types, and functions
It exports `xz_dec_init`, `xz_dec_reset`, `xz_dec_run`, and `xz_dec_end`. Under `CONFIG_XZ_DEC_MICROLZMA`, it also exports `xz_dec_microlzma_alloc`, `xz_dec_microlzma_reset`, `xz_dec_microlzma_run`, and `xz_dec_microlzma_end`. Metadata declares description, version `1.2`, authors, and dual BSD/GPL license.

## Control flow
There is no algorithmic flow. Kbuild links this file into `xz_dec.o`, and the module loader/export infrastructure makes the decoder symbols available to other kernel objects or modules.

## State and persistence behavior
The file has no mutable runtime state. Exported symbol visibility persists as part of the built kernel/module ABI.

## Dependencies and integration points
It includes `linux/module.h` and `linux/xz.h`. Its exports must match implementations in `xz_dec_stream.c` and `xz_dec_lzma2.c` and the declarations visible to consumers.

## Risks
If exports drift from enabled implementations or public headers, module builds can fail. Exporting MicroLZMA only under its config is important to avoid unresolved symbols or exposing unavailable APIs.

## Test signals
Build and modpost checks are the main signal. Module consumers should link against the exported symbols with and without `CONFIG_XZ_DEC_MICROLZMA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_dec_syms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_dec_test.c -->
# sources/distributed-fs/ceph-client/lib/xz/xz_dec_test.c

## Purpose
This optional module exposes a simple character device named `xz_dec_test` for manually feeding `.xz` files into the in-kernel decoder. It discards decompressed output but computes and logs a CRC32 of the uncompressed data.

## Important APIs, types, and functions
The module defines `xz_dec_test_open`, `xz_dec_test_release`, `xz_dec_test_write`, `xz_dec_test_init`, and `xz_dec_test_exit`. Global state includes `device_major`, `device_is_open`, decoder `state`, last decoder `ret`, 1 KiB input/output buffers, an `xz_buf` descriptor, and running CRC.

## Control flow
Module init allocates a preallocated decoder with `DICT_MAX` of 1 MiB and registers a character device. Open enforces one active user, resets decoder and buffers, and initializes CRC. Write copies user data into the input buffer, calls `xz_dec_run` while input remains or output fills, updates CRC over produced bytes, logs the decoder status, and returns either consumed byte count or an error. Release reports truncation if decoding never reached stream end. Exit unregisters the device and frees the decoder.

## State and persistence behavior
All state is module-global, so the device is single-open only. The decoder is reused across files after reset. Buffer positions in `buffers` persist across write calls for streaming input. No decompressed bytes are stored beyond the output buffer used for CRC calculation.

## Dependencies and integration points
The module depends on VFS character-device registration, usercopy, kernel CRC32, and `linux/xz.h`. Kconfig marks it as a developer/test aid rather than production functionality.

## Risks
The single global `device_is_open` flag is simple but not a full synchronization primitive for all races; this is acceptable for a developer test module but not a general device pattern. The module accepts exactly one `.xz` stream and treats trailing data as garbage. It logs to the kernel log and should not be enabled on production systems.

## Test signals
Manual testing consists of creating the device with the logged major number and writing known `.xz` files to it, then comparing logged CRC32 and decoder statuses. Negative tests should feed truncated, corrupt, unsupported-option, and trailing-garbage files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_dec_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_lzma2.h -->
# sources/distributed-fs/ceph-client/lib/xz/xz_lzma2.h

## Purpose
This header defines constants and small inline helpers for the LZMA/LZMA2 decoder. It describes range-coder parameters, LZMA state transitions, literal/match model sizes, length and distance coding geometry, and recent-distance tracking.

## Important APIs, types, and functions
Key definitions include range-coder constants `RC_SHIFT_BITS`, `RC_TOP_VALUE`, `RC_BIT_MODEL_TOTAL`, and `RC_MOVE_BITS`; position-state and literal-coder limits; `enum lzma_state`; state transition helpers `lzma_state_literal`, `lzma_state_match`, `lzma_state_long_rep`, `lzma_state_short_rep`, `lzma_state_is_literal`; match length constants; distance-slot constants; alignment constants; `PROBS_TOTAL`; and `REPS`. `lzma_get_dist_state` maps match length to distance-probability state.

## Control flow
The inline state helpers encode the LZMA finite-state model used by `xz_dec_lzma2.c`: recent literals move states back toward literal states, matches and repeats move them into match/repeat states, and short repeats get their own transition. There is no standalone runtime loop in the header.

## State and persistence behavior
The header declares constants only. Runtime state lives in `struct lzma_dec` inside `xz_dec_lzma2.c`, which uses these constants to size and update probability arrays.

## Dependencies and integration points
It is included by `xz_dec_lzma2.c`. The constants must remain consistent with the LZMA file format and with allocation/layout assumptions in `PROBS_TOTAL`.

## Risks
Changing model sizes, state transitions, or `PROBS_TOTAL` without matching decoder changes will corrupt probability indexing or output. The values are format-level constants and should be treated as fixed.

## Test signals
Any change here requires full LZMA2 decode vector coverage, invalid-distance tests, match length boundary tests, and memory-safety instrumentation over probability arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_lzma2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_private.h -->
# sources/distributed-fs/ceph-client/lib/xz/xz_private.h

## Purpose
This private header adapts the XZ decoder sources to kernel, preboot, and userspace-style builds. It maps kernel Kconfig symbols to internal decoder feature macros, defines supported decoder modes, selects BCJ support, and declares internal LZMA2/BCJ APIs.

## Important APIs, types, and functions
Important macros include `memeq`, `memzero`, `get_le32`, `DEC_IS_SINGLE`, `DEC_IS_PREALLOC`, `DEC_IS_DYNALLOC`, `DEC_IS_MULTI`, and conditional `XZ_DEC_*` feature defines. It declares `xz_dec_lzma2_create/reset/run/end` and, when BCJ is enabled, `xz_dec_bcj_create/reset/run/end`.

## Control flow
Preprocessor flow first chooses kernel versus userspace includes. In kernel non-preboot builds it includes allocation/string helpers and maps `CONFIG_XZ_DEC_*` options to decoder macros. If no decode mode macro is explicitly selected, it enables all three modes. It then derives compile-time mode predicates and enables generic `XZ_DEC_BCJ` if any architecture BCJ filter is selected.

## State and persistence behavior
There is no runtime state. The header controls compile-time feature persistence in object code and influences which branches the compiler can eliminate.

## Dependencies and integration points
It integrates Kconfig, public `linux/xz.h`, kernel allocation helpers, unaligned access, and the internal source files. `xz_dec_stream.c`, `xz_dec_lzma2.c`, `xz_dec_bcj.c`, and `xz_crc32.c` all depend on it.

## Risks
Incorrect feature macro mapping can silently remove needed filters or modes. Mode predicates are used in normal `if` statements for compile-time dead-code elimination, so they must stay boolean and side-effect free. Preboot builds have stricter include and static-data constraints.

## Test signals
Build matrix coverage across kernel module, built-in, preboot/internal CRC, BCJ-enabled/disabled, MicroLZMA-enabled/disabled, and single/prealloc/dynalloc modes is the strongest signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_stream.h -->
# sources/distributed-fs/ceph-client/lib/xz/xz_stream.h

## Purpose
This header defines `.xz` container constants and integrity-check identifiers used by the stream decoder.

## Important APIs, types, and functions
It defines `STREAM_HEADER_SIZE`, magic strings and sizes for stream header/footer, `vli_type`, `VLI_MAX`, `VLI_UNKNOWN`, `VLI_BYTES_MAX`, `enum xz_check`, and `XZ_CHECK_MAX`. In kernel builds without internal CRC32, it maps `xz_crc32` to `crc32_le` with the complement convention expected by XZ.

## Control flow
There is no runtime control flow. Preprocessor control selects whether `xz_crc32` is an internal function or a macro around the kernel CRC32 implementation.

## State and persistence behavior
The header contains constants and type aliases only. Runtime state for VLI parsing and check validation lives in `xz_dec_stream.c`.

## Dependencies and integration points
It is included by `xz_dec_stream.c` and depends on kernel `linux/crc32.h` when using the kernel CRC implementation. Values are derived from the `.xz` file format specification.

## Risks
Changing magic values, VLI limits, or check IDs would break format compatibility. Defining `vli_type` as 32-bit is documented as experimental and would constrain supported stream sizes and weaken some validation.

## Test signals
Header/footer validation, VLI boundary tests, check type handling, and builds with internal versus kernel CRC32 implementations are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/xz/xz_stream.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_deflate/Makefile -->
# sources/distributed-fs/ceph-client/lib/zlib_deflate/Makefile

## Purpose
This Makefile builds the kernel's modified zlib deflate compression support, which performs memory allocation ahead of time. It complements `lib/zlib_inflate` for decompression.

## Important build targets
`obj-$(CONFIG_ZLIB_DEFLATE) += zlib_deflate.o` builds the composite object when deflate support is enabled. `zlib_deflate-objs := deflate.o deftree.o deflate_syms.o` composes the compressor implementation, tree logic, and exported symbols.

## Control flow
Kbuild includes this directory's deflate object only when `CONFIG_ZLIB_DEFLATE` is selected. The composite object links the implementation pieces into one kernel object or module target.

## State and persistence behavior
There is no runtime state in the Makefile. Build selection persists through the kernel configuration.

## Dependencies and integration points
It integrates with Kconfig's `CONFIG_ZLIB_DEFLATE` symbol and with kernel consumers that use zlib compression APIs exported by `deflate_syms.o`.

## Risks
If object composition drifts from source exports, link or modpost failures will occur. Since this is the compression side only, consumers requiring inflate must select the separate zlib inflate support.

## Test signals
Build coverage with `CONFIG_ZLIB_DEFLATE=y/m/n`, module link checks for exported deflate APIs, and compression round-trip tests through zlib inflate are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/zlib_deflate/Makefile -->
