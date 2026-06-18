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
