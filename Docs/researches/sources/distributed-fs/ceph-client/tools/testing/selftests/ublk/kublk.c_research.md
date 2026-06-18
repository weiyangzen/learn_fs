# sources/distributed-fs/ceph-client/tools/testing/selftests/ublk/kublk.c

## Purpose
`kublk.c` is the main userspace ublk test daemon and CLI. It creates, starts, stops, recovers, lists, and resizes ublk devices; launches I/O handler threads; dispatches ublk requests to target backends; supports batch I/O, zero-copy, auto buffer registration, user-copy, integrity metadata, per-I/O daemon distribution, safe stop, and shared-memory zero-copy registration.

## Important APIs, Types, and Functions
Control wrappers include `ublk_ctrl_*()` functions for add/delete/start/stop/try-stop/recovery/get-info/set/get-params/features/update-size/quiesce. Device/thread setup includes `ublk_ctrl_init()`, `ublk_dev_prep()`, `ublk_queue_init()`, `ublk_thread_init()`, `ublk_start_daemon()`, `ublk_io_handler_fn()`, and `ublk_process_io()`. I/O paths include `ublk_queue_io_cmd()`, `ublk_submit_fetch_commands()`, `ublk_handle_uring_cmd()`, `ublk_handle_cqe()`, and target CQE dispatch. CLI commands are `add`, `recover`, `del`, `stop`, `list`, `features`, `update_size`, and `quiesce`.

## Control Flow
`main()` parses global and target-specific options into `struct dev_ctx`, validates incompatible copy modes and integrity requirements, lets the chosen target parse its options, and dispatches to a command. `cmd_dev_add()` usually double-forks a daemon, using shared memory and eventfd to report the allocated device ID back to the parent. `__cmd_dev_add()` queries kernel features, adds or starts recovery, initializes target and queues, starts handler threads, sets params, starts the device, and waits for threads to exit. Non-batch threads issue fetch/commit uring commands per tag; batch threads use batch prep/fetch/commit helpers. Delete/stop/list/update/quiesce commands issue synchronous control uring commands.

## State and Persistence
Runtime state is stored in `struct ublk_dev`, queues, thread rings, open fds, mapped command buffers, shared-memory registration table, and child daemon process state. Persistent state may be backing files and kernel ublk devices. The daemon creates `/run/ublk/ublkb<id>.sock` for shared-memory registration and removes it on shutdown.

## Dependencies and Integration Points
It depends on `/dev/ublk-control`, `/dev/ublkcN`, `/dev/ublkbN`, Linux ublk UAPI, liburing, pthreads, SysV shared memory, eventfd, inotify, Unix sockets, and target ops from `null.c`, `file_backed.c`, `stripe.c`, and `fault_inject.c`. Shell tests call this binary through `test_common.sh`.

## Risks
The daemon is concurrency-heavy: failures can stem from queue/thread mapping, fixed file indexes, CQE accounting, daemon death, recovery race windows, and cleanup of forked children. It rejects several incompatible option combinations, but newer kernel features require `feat_map` updates or `test_generic_13.sh` fails. Shared-memory zero-copy depends on fd passing, mmap lifetime, and registered virtual address matching.

## Test Signals
Signals come from shell tests: successful add/list/del, fio and filesystem I/O over targets, correct feature listing, update-size propagation, safe-stop busy behavior, per-I/O task balancing, fast daemon-death cleanup, and recovery teardown.
