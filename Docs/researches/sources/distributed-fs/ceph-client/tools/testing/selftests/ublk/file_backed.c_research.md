# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/file_backed.c

## Purpose
This file implements the `loop` ublk target, mapping ublk read/write/flush requests to a single data backing file, with optional integrity metadata file, zero-copy, auto buffer registration, shared-memory zero-copy, and user-copy integration.

## Important APIs, Types, and Functions
`ublk_to_uring_op()` maps ublk read/write to io_uring ops. `loop_queue_flush_io()`, `loop_queue_shmem_zc_io()`, `loop_queue_tgt_rw_io()`, and `loop_queue_tgt_io()` prepare target SQEs. `ublk_loop_queue_io()` queues target work. `ublk_loop_io_done()` aggregates completion results. `ublk_loop_memset_file()` initializes integrity metadata. `ublk_loop_tgt_init()` opens backing files and configures `struct ublk_params`.

## Control Flow
For read/write, the target chooses shared-memory zero-copy if `UBLK_IO_F_SHMEM_ZC` is set, otherwise handles integrity I/O to a second file when requested, then either submits direct read/write, auto-zc fixed-buffer operations, or explicit register/read/unregister sequences for zero-copy. Flush maps to `fsync`. Completion records the shortest data result, translates integrity bytes back to data length when needed, accounts for skipped buffer-register CQEs, and commits the ublk request when all target SQEs complete.

## State and Persistence
Persistent state is the backing data file and optional integrity file. Runtime state includes per-I/O buffers, integrity buffers, shared-memory registrations in `shmem_table`, and open fds stored in `dev->fds`.

## Dependencies and Integration Points
It depends on `common.c` backing file helpers, `kublk.c` shared-memory registration, liburing, ublk UAPI flags, and shell tests using `-t loop`, `-g`, `--auto_zc`, batch mode, and integrity options.

## Risks
Correctness depends on buffer alignment, fixed-file indexes, shared-memory index/offset decoding, and matching data/integrity file sizes. Unsupported discard/write-zeroes return `-ENOTSUP`. Auto-zc fallback is rejected at init.

## Test Signals
Filesystem mount tests and fio verify tests over loop-backed ublk devices signal correct data path behavior. Integrity tests depend on proper metadata sizing and initialization.
