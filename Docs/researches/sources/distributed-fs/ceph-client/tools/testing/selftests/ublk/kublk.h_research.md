# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/kublk.h

## Purpose
This internal header defines the shared data structures, constants, target interface, inline helpers, and cross-file prototypes for the `kublk` ublk selftest daemon.

## Important APIs, Types, and Functions
Major types include `struct dev_ctx`, `struct ublk_ctrl_cmd_data`, `struct ublk_io`, `struct ublk_tgt_ops`, `struct ublk_tgt`, `struct ublk_queue`, `struct ublk_thread`, `struct ublk_dev`, and batch/shmem helper structures. Inline helpers cover batch checks, integrity length conversion, user-copy offsets, encoded `user_data`, SQE allocation, fixed/raw fd mapping, buffer register commands, I/O completion, queue flags, and target dispatch accounting.

## Control Flow
The header has no standalone control flow, but its inline helpers are on hot paths. `build_user_data()` and decoders route CQEs to queue/tag/op/target handlers. `ublk_complete_io()` chooses batch commit or ordinary commit/fetch command. `ublk_queued_tgt_io()` either completes failed target setup immediately or tracks target SQE count.

## State and Persistence
It defines runtime state layouts for all ublk daemon objects. Persistent behavior is indirect through target backing files and kernel devices.

## Dependencies and Integration Points
It includes liburing, pthread/semaphore, mmap/ioctl/inotify/eventfd, `ublk_dep.h`, Linux `ublk_cmd.h`, and `utils.h`. All ublk C files include it.

## Risks
Bit packing in `build_user_data()` is central to CQE correctness; queue count/tag/op width assumptions are asserted but must stay aligned with constants. Inline buffer-index helpers must match batch and zero-copy registration behavior.

## Test Signals
Successful compilation and all ublk tests exercise this header. Failures often manifest as bad CQE routing, wrong buffer indexes, or incorrect completion accounting.
