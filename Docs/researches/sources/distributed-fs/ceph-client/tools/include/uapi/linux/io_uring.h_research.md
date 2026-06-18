# sources/distributed-fs/ceph-client/tools/include/uapi/linux/io_uring.h

Purpose: defines the complete io_uring userspace ABI: submission/completion entries, setup flags, operation codes, mmap ring offsets, enter/register flags, registered resource structures, probes, restrictions, provided buffers, and ancillary result formats.

Important APIs/types: `io_uring_sqe` encodes per-operation input through unions for fd, offsets, buffers, flags, fixed-file slots, socket/xattr/splice/msg-ring/uring-cmd fields, and optional 128-byte command data. `enum io_uring_op` covers reads/writes, fsync, poll, timeouts, sockets, open/close/statx, splice/tee, filesystem operations, xattrs, msg ring, uring command, zero-copy send, multishot read/recv, waitid, and futex operations. `io_uring_cqe` returns `user_data`, result, and flags. Ring layout types are `io_sqring_offsets`, `io_cqring_offsets`, and `io_uring_params`. Register APIs use resource update/register structures, probe structures, restrictions, buffer rings, getevents args, sync cancel, file index ranges, and recvmsg output.

Control flow, state, and persistence: userspace calls `io_uring_setup`, mmaps SQ/CQ/SQE regions, fills SQEs, advances ring indices, calls `io_uring_enter`, and consumes CQEs. Registered files/buffers/personalities/rings and provided-buffer groups persist until unregistered or ring close.

Dependencies and integration points: depends on `fs.h`, types, and time types. It integrates VFS, block, networking, futex, eventfd, io-wq workers, fixed resources, and liburing.

Risks and test signals: risks include ABI union field misuse per opcode, memory-ordering bugs in shared rings, feature-flag assumptions, CQ overflow, multishot lifetime handling, fixed-resource index errors, and setup flag incompatibilities. Tests should run opcode probes, setup variants, fixed files/buffers, linked operations, cancellation, buffer selection, multishot operations, ring fd registration, and 32-byte CQE/128-byte SQE modes.
