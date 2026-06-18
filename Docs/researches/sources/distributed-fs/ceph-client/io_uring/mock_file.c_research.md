<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/mock_file.c -->
# sources/distributed-fs/ceph-client/io_uring/mock_file.c

## Purpose
`mock_file.c` provides a testing-only misc device, `/dev/io_uring_mock`, that exposes `uring_cmd` manager commands to create anonymous mock files and probe supported features. Created mock files implement controlled read/write behavior, optional poll support, optional NOWAIT support, delayed asynchronous completions, fixed size bounds, and a command for copying registered buffers to/from user memory.

## Important APIs, Types, and Functions
- `struct io_mock_file` stores size, artificial read/write delay, pollability, and a waitqueue.
- `struct io_mock_iocb` stores delayed kiocb completion state and an hrtimer.
- `iou_mock_mgr_cmd()` dispatches manager `IORING_MOCK_MGR_CMD_PROBE` and `IORING_MOCK_MGR_CMD_CREATE`.
- `io_create_mock_file()` validates `io_uring_mock_create`, creates an anonymous mock file, configures fops and modes, and publishes an fd back to userspace.
- `io_mock_read_iter()` and `io_mock_write_iter()` implement bounded zero-fill reads and advancing writes, optionally delayed with `io_mock_delay_rw()`.
- `io_mock_cmd()` dispatches per-file mock commands such as `IORING_MOCK_CMD_COPY_REGBUF`.
- `io_cmd_copy_regbuf()` imports fixed registered vectors from an io_uring command and copies between those iterators and a userspace buffer.
- `io_mock_init()`/`io_mock_exit()` register/deregister the misc device.

## Control Flow
Users with `CAP_SYS_ADMIN` open the misc device and issue a manager uring command. Probe requires an all-zero `io_uring_mock_probe` input and returns feature bits. Create copies `io_uring_mock_create`, validates flags/reserved fields, caps file size at 1 GiB and delay at 1 second, allocates `io_mock_file`, picks poll or non-poll fops, creates an anonymous inode file, sets read/write/seek modes plus optional `FMODE_NOWAIT`, copies the output fd into the user struct, then publishes the fd.

Read/write operations check `ki_pos + len <= size`. Reads zero the destination iterator immediately; writes advance the source iterator immediately for no-delay mode. With `rw_delay_ns`, both create an hrtimer-backed `io_mock_iocb`, return `-EIOCBQUEUED`, and later call `ki_complete()` with the requested length.

The registered-buffer copy command imports fixed vectors with `io_uring_cmd_import_fixed_vec()` and then loops through the iterator in page-sized chunks, copying from iter to user or user to iter depending on `IORING_MOCK_COPY_FROM`.

## State and Persistence Behavior
The misc device is module-global. Each created anonymous file owns an `io_mock_file` until release. Delayed operations allocate one `io_mock_iocb` per queued IO and free it on hrtimer completion. The module deliberately taints the kernel with `TAINT_TEST` when creating mock files.

## Dependencies and Integration Points
This module integrates with the io_uring command path, registered buffer import, anonymous inodes, miscdevice framework, hrtimers, iterators, poll, and module init/exit. It is a test helper rather than part of production ring operation.

## Risks and Edge Cases
- Delayed IO uses hrtimer completion state; cancellation semantics depend on the broader kiocb/io_uring machinery and the file does not explicitly cancel timers on release.
- Copying registered buffers through a temporary page loop must handle short copies and user faults; current return is bytes copied or `-EFAULT` when zero bytes copied.
- Poll fops always report readable/writable and do not model readiness transitions, so tests must understand it is synthetic.
- Manager commands require `CAP_SYS_ADMIN` but created files can exercise edge cases that normal files may not expose.

## Test Signals
Tests should cover manager permission checks, probe, create validation, NOWAIT flag behavior, pollable vs non-pollable fops, size-bound read/write errors, delayed `-EIOCBQUEUED` completion, registered buffer copy in both directions, and release cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/mock_file.c -->
