# sources/distributed-fs/ceph-client/ipc/msg.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/msg.c` implements System V message queues: queue creation, removal, control operations, blocking send/receive, message selection by type, permission/security checks, namespace initialization, proc reporting, and compat syscall support. The source was read as a complete 1376-line file.

## Important APIs, Types, and Functions

`struct msg_queue` stores IPC permissions, timestamps, byte/message counts, byte limit, sender/receiver pids, queued messages, and sleeping receiver/sender lists. `struct msg_receiver` tracks a blocked `msgrcv()` selection and destination constraints. `struct msg_sender` tracks a blocked `msgsnd()` waiting for queue space.

Public syscall helpers are `ksys_msgget()`, `ksys_msgsnd()`, `ksys_msgrcv()`, and the `msgctl` syscall path through `ksys_msgctl()`. Core helpers include `newque()`, `freeque()`, `msgctl_down()`, `msgctl_info()`, `msgctl_stat()`, `do_msgsnd()`, `pipelined_send()`, `convert_mode()`, `find_msg()`, and `do_msgrcv()`. Namespace hooks are `msg_init_ns()`, `msg_exit_ns()`, and `msg_init()`.

## Control Flow

`msgget` delegates to `ipcget()` with `newque()` for creation and LSM association for existing queues. `msgsnd` copies the user message via `load_msg()`, validates type and size, locks the target queue under RCU, checks write permission and LSM policy, waits if the queue is full unless `IPC_NOWAIT`, then either directly hands the message to a matching sleeping receiver or appends it to `q_messages`.

`msgrcv` converts the requested type and flags into a search mode: first message, exact type, not-equal type, lowest type less-or-equal, or `MSG_COPY` ordinal lookup. It scans the queue with LSM receive checks, unlinks and accounts a matching message unless `MSG_COPY` is used, or sleeps as a `msg_receiver`. A sender can complete a sleeping receiver with a release-store to `r_msg`, allowing the receiver to return without relocking when safe.

`msgctl` handles info/stat commands, permission updates, queue-byte limit changes, and removal. `IPC_RMID` expunges receivers, wakes senders with `-EIDRM`, removes the queue id, and frees all queued messages and pid references.

## State and Persistence Behavior

Message queue objects live in `ns->ids[IPC_MSG_IDS]` and persist until `IPC_RMID` or namespace teardown. Queued bytes and headers are mirrored in per-namespace percpu counters for `MSG_INFO`. Timestamps and last-pid fields are updated on send, receive, and control changes. Message payloads are allocated in segmented kernel memory and freed after receive, copy failure cleanup, queue removal, or namespace exit.

## Dependencies and Integration Points

The file integrates generic SysV IPC id/key management from `util.h`, LSM hooks (`security_msg_queue_*`), audit, percpu counters, RCU/id locks, pid namespaces for proc output, compat permission conversion, and shared message allocation/copy helpers from `msgutil.c`.

## Risks and Edge Cases

The lockless receiver wake path depends on the documented `MSG_BARRIER` ordering and `wake_q_add_safe()`. Queue-full logic uses both byte count and message count against `q_qbytes`, preserving historical semantics. `MSG_COPY` is only valid with checkpoint/restore support, `IPC_NOWAIT`, and without `MSG_EXCEPT`. Type conversion must handle `LONG_MIN`. Permission changes can make sleeping receivers invalid and must expunge them with `-EAGAIN`.

## Test Signals

Tests should cover create/find semantics, `IPC_CREAT|IPC_EXCL`, permission denial, queue full blocking and wakeup order, direct sender-to-receiver handoff, message type selection modes, `MSG_NOERROR`, `MSG_COPY`, `IPC_STAT`/`MSG_STAT_ANY`, `IPC_SET` byte-limit changes, `IPC_RMID` with blocked tasks, namespace isolation, proc output, and compat send/receive/control paths.
