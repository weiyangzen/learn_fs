# sources/distributed-fs/ceph-client/fs/dlm/requestqueue.c

## Purpose
`requestqueue.c` stores normal DLM lock messages received while a lockspace is stopped for recovery, then replays or purges them after recovery makes normal locking safe again.

## Important APIs, Types, And Functions
The internal type is `struct rq_entry`, which stores the sending node, low 32 bits of the recovery sequence, and an inline copy of `struct dlm_message` plus extra payload. Exports are `dlm_add_requestqueue()`, `dlm_process_requestqueue()`, and `dlm_purge_requestqueue()`.

## Control Flow
`dlm_add_requestqueue()` copies a received message and appends it to `ls_requestqueue`. `dlm_process_requestqueue()` runs after locking is enabled, pops entries in FIFO order, logs message identifiers, calls `dlm_receive_message_saved()`, frees entries, and schedules between entries. If locking stops again, it aborts with `-EINTR`. When the queue drains it clears `LSFL_RECV_MSG_BLOCKED`.

`dlm_purge_requestqueue()` removes entries that are unsafe or invalid after recovery: messages from removed nodes, directory remove/lookup/lookup-reply messages, all messages if the lockspace is being freed, and all messages in no-directory mode.

## State And Persistence
Queued messages are heap-allocated and kept on `ls->ls_requestqueue` under `ls_requestqueue_lock`. They persist only across the active recovery window.

## Dependencies And Integration Points
The queue integrates with `dlm_ls_stop()`/`enable_locking()` in membership/recoverd, lock receive replay through `dlm_receive_message_saved()`, directory rebuild semantics, and errno conversion logging via `util.c`.

## Risks
The variable-length message copy depends on trusted `h_length`; callers should have already validated packet length. Purge policy is conservative for directory messages because directory contents are rebuilt. Replay under the requestqueue lock can interact with lock receive behavior, so comments describe expected blocking semantics.

## Test Signals
Test messages arriving during recovery, replay after recovery, purge after node removal, directory lookup resend behavior, no-directory mode purge, and recovery interruption while replay is active.
