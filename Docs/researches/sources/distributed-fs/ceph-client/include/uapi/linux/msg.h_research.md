# sources/distributed-fs/ceph-client/include/uapi/linux/msg.h

## Purpose
Defines System V message queue UAPI constants, legacy structs, message buffer layout, info struct, and default queue/message limits.

## Important APIs, Types, And Functions
Exports `MSG_STAT`, `MSG_INFO`, `MSG_STAT_ANY`, `MSG_NOERROR`, `MSG_EXCEPT`, `MSG_COPY`, legacy `msqid_ds`, `msgbuf`, `msginfo`, and defaults `MSGMNI`, `MSGMAX`, `MSGMNB`, plus obsolete pool/map constants.

## Control Flow
Userspace uses msgsnd/msgrcv/msgctl. Receive flags control truncation, type exclusion, and copy-without-remove behavior. `msgctl` info/stat commands return queue metadata through legacy or architecture-specific 64-bit structs.

## State, Persistence, And Dependencies
State persists in IPC namespaces as message queue objects and queued messages. Depends on `linux/ipc.h` and includes `asm/msgbuf.h`.

## Integration Points
Used by SysV IPC libraries, `ipcs`, checkpoint/restore tools, and compatibility layers.

## Risks
Legacy structs are retained for ABI compatibility and contain unused pointer fields. Defaults can be changed by sysctl, and arithmetic around limits must avoid overflow.

## Test Signals
Validate send/receive flags, `MSG_COPY`, msgctl stat/info, namespace limits, queue byte accounting, permission checks, and 32/64-bit ABI compatibility.
