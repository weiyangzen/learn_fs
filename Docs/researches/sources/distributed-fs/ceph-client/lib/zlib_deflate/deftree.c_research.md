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
