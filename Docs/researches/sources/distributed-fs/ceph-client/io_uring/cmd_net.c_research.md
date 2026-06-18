# sources/distributed-fs/ceph-client/io_uring/cmd_net.c

## Purpose
`cmd_net.c` implements socket-specific io_uring command operations: socket queue ioctls, getsockopt/setsockopt, TX timestamp multishot CQEs, and getsockname/peername support.

## Important APIs, Types, And Functions
- `io_uring_cmd_sock()` dispatches `cmd->cmd_op` to socket command handlers and is exported GPL.
- `io_uring_cmd_get_sock_ioctl()` calls protocol `ioctl` for `SIOCINQ`/`SIOCOUTQ`.
- `io_uring_cmd_getsockopt()` and `io_uring_cmd_setsockopt()` bridge SQE opt fields into socket option helpers.
- `io_uring_cmd_timestamp()` polls the socket error queue and posts CQE32 timestamp records.
- `io_uring_cmd_getsockname()` validates SQE fields and calls `do_getsockname()` for local or peer addresses.

## Control Flow
The dispatcher uses the socket from `cmd->file->private_data`. Timestamp handling requires CQE32, arms multishot poll for `EPOLLERR`, drains timestamp-only skbs from `sk_error_queue`, posts one CQE pair per timestamp, and requeues unposted skbs.

## State And Persistence
No persistent module state is stored. Operations can consume entries from a socket error queue, return socket option values to user memory, and post multishot CQEs.

## Dependencies And Integration Points
The file depends on net socket internals, errqueue timestamp helpers, io_uring command infrastructure, multishot CQE32 posting, socket UAPI command opcodes, and compat handling via issue flags.

## Risks And Edge Cases
TX timestamp requires CQE32 and rejects payload skbs. Error-queue locking and requeueing must preserve skbs when CQE posting stops. Only `SOL_SOCKET` getsockopt is supported here; unsupported protocol/levels return `-EOPNOTSUPP`. SQE padding validation prevents ABI ambiguity.

## Test Signals
Socket io_uring command tests should cover queue depth ioctls, getsockopt/setsockopt parity, timestamp multishot delivery with CQE32, requeue behavior on partial posting, getsockname/peername, compat mode, and invalid SQE fields.
