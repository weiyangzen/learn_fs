
# sources/distributed-fs/openafs/src/usd/test/usd_test.c

`usd_test.c` is a destructive/manual integration test for the USD tape-device abstraction. It opens a supplied tape device read/write with a write lock, prepares and rewinds it, writes blocks and file marks, reads back content, exercises forward/backward file spacing, shuts down the tape, and closes the USD handle.

Important helpers are `err_exit`, `bufeql`, `Rewind`, `WriteEOF`, `ForwardSpace`, `BackSpace`, `PrepTape`, `ShutdownTape`, and `PrintTapePos`. The main flow writes ten 1024-byte blocks, writes one EOF mark, rewinds and reads ten blocks, writes five data/filemark pairs, tests `FSF` by reading expected marker bytes, tests `BSF` plus `FSF`, then shuts down and closes.

State and persistence are on the target tape device. The test intentionally changes media contents and assumes tape semantics. It uses `USD_IOCTL_TAPEOPERATION`, `USD_READ`, `USD_WRITE`, `USD_SEEK`, and `USD_CLOSE`; Windows position reporting calls `GetTapePosition` directly via `hTape->handle`, while Unix uses `USD_SEEK(SEEK_CUR)`.

Risks include destructive media writes, uninitialized buffer contents in the first write/read comparison except for later marker bytes, recursion concerns avoided in `ShutdownTape`, and platform/device dependence. Test signals are explicit console pass/fail messages, transferred byte counts, data equality, tape operation return codes, and optional position debug output via `USDTEST_DEBUG`.
