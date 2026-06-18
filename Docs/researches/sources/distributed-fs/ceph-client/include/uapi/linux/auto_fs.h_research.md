<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/auto_fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/auto_fs.h

## Purpose
Defines the classic autofs pipe packet and ioctl ABI for protocol versions 3 through 5.

## Important APIs, Types, And Functions
Exports protocol version/subversion constants, `autofs_wqt_t`, packet header/missing/expire structs, legacy ioctls `AUTOFS_IOC_READY`, `FAIL`, `CATATONIC`, `PROTOVER`, `SETTIMEOUT`, `EXPIRE`, v4/v5 expire/missing packet types, mount type helpers, notification enum, v5 packet unions, and `AUTOFS_IOC_EXPIRE_MULTI`, `PROTOSUBVER`, `ASKUMOUNT`.

## Control Flow
Kernel autofs sends missing/expire packets to the daemon through a pipe. The daemon mounts or expires paths, then completes wait tokens with ready/fail ioctls. Additional ioctls negotiate protocol versions, timeout, multi-expire, and umount readiness.

## State And Persistence
State is per autofs mount: protocol version, wait queue tokens, pending path packets, mount type, timeout, and daemon pipe/catatonic status. It is runtime VFS/daemon coordination state.

## Dependencies And Integration Points
Depends on Linux types/limits and userspace ioctl definitions. Integrates with automount daemons, VFS path lookup, direct/indirect/offset mount types, and the newer control device ABI.

## Risks And Edge Cases
`autofs_wqt_t` size is architecture-sensitive to preserve compat ABI. Path name length is fixed at `NAME_MAX+1`. Token completion ordering, daemon death/catatonic mode, and direct vs indirect packet interpretation are common hazards.

## Test Signals
Protocol negotiation, missing and expire packet delivery, ready/fail completion, timeout setting, multi-expire behavior, direct/indirect/offset trigger tests, compat type-size checks, and daemon crash recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/auto_fs.h -->
