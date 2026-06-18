<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/aio_abi.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/aio_abi.h

## Purpose
Defines the Linux native asynchronous I/O ABI structures shared by `io_submit`, `io_getevents`, and related system calls.

## Important APIs, Types, And Functions
`aio_context_t` is the userspace context handle. `enum IOCB_CMD_*` identifies pread, pwrite, fsync, fdsync, poll, noop, preadv, and pwritev operations. `IOCB_FLAG_RESFD` and `IOCB_FLAG_IOPRIO` control eventfd and ioprio usage. `struct io_event` reports completion data/object/result fields. `struct iocb` describes one submitted operation and is exactly 64 bytes.

## Control Flow
Userspace creates an AIO context, fills one or more `iocb` records, submits pointers to the kernel, and later reads `io_event` completions. The kernel stores an internal request key and returns results through the event queue and optional eventfd.

## State And Persistence
State is per AIO context: queued requests, completion events, eventfd notifications, and kernel-side request keys. It is transient and tied to process/file lifetime.

## Dependencies And Integration Points
Depends on Linux types, fs `RWF_*` flags, and architecture byte order. Integrates with filesystem/block I/O, eventfd, polling, and libc/libaio wrappers.

## Risks And Edge Cases
The byte-order-dependent placement of `aio_key` and `aio_rw_flags`, 64-bit pointer/offset fields, unsupported opcode values, eventfd lifetime, and priority flag interpretation are ABI-sensitive.

## Test Signals
Structure size/layout tests, pread/pwrite completion tests, eventfd signaling, vectored I/O, poll/noop behavior, endian compile checks, and invalid opcode/flag rejection provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/aio_abi.h -->
