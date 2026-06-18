<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/msg_ring.h -->
# sources/distributed-fs/ceph-client/io_uring/msg_ring.h

## Purpose
`msg_ring.h` declares the msg-ring operation interface used by the opcode table and synchronous callers.

## Important APIs, Types, and Functions
- `io_uring_sync_msg_ring()` sends a data message directly from a prepared SQE-like structure.
- `io_msg_ring_prep()` prepares an async `IORING_OP_MSG_RING` request.
- `io_msg_ring()` issues the prepared request.
- `io_msg_ring_cleanup()` releases held resources such as source files for SEND_FD.

## Control Flow
The core request path calls prep, then issue, then cleanup through `io_cold_defs` if `REQ_F_NEED_CLEANUP` remains. Synchronous callers bypass request allocation and call `io_uring_sync_msg_ring()` for data-only messages.

## State and Persistence Behavior
The header does not define persistent state; `msg_ring.c` stores transient payload in the request command area.

## Dependencies and Integration Points
It depends on `struct io_kiocb`, `struct io_uring_sqe`, and issue flags from core io_uring types. It is consumed by `io_uring.c`, `opdef.c`, and any sync msg-ring caller.

## Risks and Edge Cases
The cleanup declaration is essential because SEND_FD can hold a source file across async retry. Missing cleanup table registration would leak file refs.

## Test Signals
Build linkage plus runtime msg-ring data and SEND_FD tests validate the header contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/msg_ring.h -->
