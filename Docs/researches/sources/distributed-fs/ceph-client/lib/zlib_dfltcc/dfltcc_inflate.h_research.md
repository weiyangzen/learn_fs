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
