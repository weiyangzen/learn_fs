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
