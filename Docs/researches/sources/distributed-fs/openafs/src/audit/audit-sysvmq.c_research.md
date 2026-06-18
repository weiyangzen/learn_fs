# sources/distributed-fs/openafs/src/audit/audit-sysvmq.c

## Purpose
`audit-sysvmq.c` implements a SysV message queue audit backend when `HAVE_SYS_IPC_H` is available.

## Important APIs, types, and functions
`struct my_msgbuf` matches `msgsnd` layout with `mtype` and `mtext[OSI_AUDIT_MAXMSG]`. `struct mqaudit_stats` tracks total, truncated, and lost messages. `struct sysvmq_context` stores the queue id, reusable message buffer, and stats. Callback implementations are exported as `audit_sysvmq_ops`.

## Control flow
`open_file` creates a filesystem token for `ftok`, opens or creates the message queue, and attempts to raise `msg_qbytes` to 2 MiB. `send_msg` truncates overlarge records, copies a NUL-terminated payload into the queue buffer, and calls `msgsnd(..., IPC_NOWAIT)`, incrementing lost or truncated stats. `print_interface_stats` reports counters. `close_interface` frees only the local context, not the system message queue.

## State and persistence
The backend persists messages in a kernel SysV message queue keyed by `ftok(fileName, 1)`. The ftok file may be created with owner read/write mode. Queue lifetime is not removed on backend close.

## Dependencies and integration points
It is conditionally compiled and registered in `audit.c` when SysV IPC headers exist. Consumers can select it via `-audit-interface sysvmq` or `sysvmq:<filespec>` auditlog syntax.

## Risks
`ftok` key collisions are possible. Queue size changes may fail silently if permissions are insufficient. Nonblocking sends can drop messages under load; stats expose this but callers do not retry. The persistent queue may outlive the daemon and require external cleanup.

## Test signals
Test queue creation, existing queue reuse, permission failures, message truncation, full-queue loss accounting, stat output, and builds without `HAVE_SYS_IPC_H`.
