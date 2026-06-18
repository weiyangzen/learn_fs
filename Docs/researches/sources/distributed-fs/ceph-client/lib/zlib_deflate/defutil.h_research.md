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
