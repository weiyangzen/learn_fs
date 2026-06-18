# sources/distributed-fs/openafs/src/rx/xdr_rec.c

## Purpose
`xdr_rec.c` implements record-marked XDR streams over a TCP-like read/write handle. It supports Sun RPC record fragments with a high-bit last-fragment marker and 31-bit fragment length.

## Important APIs, Types, and Functions
- `RECSTREAM` stores input/output buffers, fragment state, callbacks, and sizes.
- `xdrrec_create()` allocates buffers and initializes backend ops.
- Backend ops implement int32/byte read-write, position, inline, and destroy behavior.
- Exported record controls: `xdrrec_skiprecord()`, `xdrrec_eof()`, and `xdrrec_endofrecord()`.
- Internal helpers: `flush_out()`, `fill_input_buf()`, `get_input_bytes()`, `set_input_fragment()`, `skip_input_bytes()`, and `fix_buf_size()`.

## Control Flow
Writes buffer data behind a fragment header; `xdrrec_endofrecord()` either flushes with `LAST_FRAG` or starts another in-buffer fragment. Reads consume fragment bytes, reading new fragment headers when needed. `skiprecord` discards remaining fragments until record alignment is restored.

## State and Persistence
The `XDR` handle owns a heap-allocated `RECSTREAM` plus input/output buffers until `XDR_DESTROY`. Fragment counters (`fbtbc`, `last_frag`, `frag_sent`) persist across calls and define the current record boundary.

## Dependencies and Integration Points
Used for RPC-over-stream transports that need record marking. It depends on caller-provided `readit` and `writeit` callbacks and generic XDR routines dispatch through its ops vector.

## Risks and Edge Cases
`xdrrec_create()` returns `void` and silently leaves partially allocated state on allocation failure. Several pointer differences are cast through 32-bit integer types, which is risky on 64-bit systems. The position functions assume `tcp_handle` can be cast to an fd for `lseek`, which is not valid for every opaque handle.

## Test Signals
Round-trip records with single and multiple fragments, verify `skiprecord` alignment, test EOF lookahead, force small send/receive buffers, and simulate short read/write callback failures.
