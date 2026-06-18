<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/msg_ring.c -->
# sources/distributed-fs/ceph-client/io_uring/msg_ring.c

## Purpose
`msg_ring.c` implements `IORING_OP_MSG_RING`, allowing one io_uring instance to post data CQEs into another ring or transfer a registered file into another ring's fixed-file table. It also implements the synchronous data-message helper used outside normal request context.

## Important APIs, Types, and Functions
- `struct io_msg` is the per-request command payload: target/source files, remote task_work, user data, len, command, source fd, destination fd or CQE flags, and message flags.
- `io_msg_ring_prep()` validates SQE fields and fills `io_msg`.
- `io_msg_ring()` dispatches `IORING_MSG_DATA` and `IORING_MSG_SEND_FD` after verifying the target file is an io_uring fd.
- `io_uring_sync_msg_ring()` sends a data CQE synchronously to a target ring fd.
- `io_msg_ring_cleanup()` drops a held source file for SEND_FD failures/cancellations.
- `__io_msg_ring_data()` posts a data CQE directly, through target task_work, or under IOPOLL target locking.
- `io_msg_send_fd()` grabs a source fixed file and installs it into the target fixed-file table, possibly via target submitter task_work.

## Control Flow
Prep rejects `buf_index` and `personality`, reads user data from `sqe->off`, message length, command, source fixed fd, destination fixed slot, and msg-ring flags. Data messages reject source fd and unsupported flags, reject disabled target rings, and then choose a posting mode. Rings with `IO_RING_F_TASK_COMPLETE` require remote task_work, so `io_msg_data_remote()` allocates a fresh request from `req_cachep`, initializes it as a NOP-like aux completion, bumps the target context ref, and queues remote task_work. Other rings use `io_post_aux_cqe()` directly, with external locking for IOPOLL rings.

SEND_FD rejects nonzero len and same source/target context. It grabs the source fixed file from the source ring's file table if not already held, marks `REQ_F_NEED_CLEANUP`, rejects disabled target rings, and either queues target submitter task_work for task-complete rings or installs immediately. `io_msg_install_complete()` locks the target context, calls `__io_fixed_fd_install()`, clears cleanup ownership on success, and optionally posts a target CQE unless `IORING_MSG_RING_CQE_SKIP` is set.

## State and Persistence Behavior
Data messages create transient CQEs in the target ring. Remote data completion temporarily allocates an `io_kiocb` and frees it with `kfree_rcu()` after the aux CQE is added. SEND_FD holds `msg->src_file` across retries/remote task_work and clears it only after successful install; cleanup fputs it on failure. The target ring's fixed-file table persists the installed file reference.

## Dependencies and Integration Points
This module depends on core CQE posting, task_work, request cache, fixed-file resource lookup/install, ring fd verification, and target context locking. It integrates with `opdef.c` as `IORING_OP_MSG_RING`, with cleanup registered in `io_cold_defs`, and with core ring fd resolution through `io_is_uring_fops()`.

## Risks and Edge Cases
- Lock ordering between source and target rings avoids deadlock by trylocking the target when the source lock is already held; `-EAGAIN` punts to io-wq.
- Target rings with `IORING_SETUP_R_DISABLED` are rejected before submitter-task access.
- If target CQE posting fails after SEND_FD install, the file is already visible in the target table and the sender receives `-EOVERFLOW`.
- Remote task_work can fail with `-EOWNERDEAD` if the target submitter task is exiting.
- SEND_FD cannot target the same ring and fixed destination slot rules are enforced by the fixed-file table.

## Test Signals
Tests should cover data CQE posting to normal, IOPOLL, and task-complete rings; CQE flag passing; disabled target rejection; synchronous msg ring data; SEND_FD installation, CQE skip, source cleanup on failure, same-ring rejection, target overflow, and trylock `-EAGAIN` retry behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/msg_ring.c -->
