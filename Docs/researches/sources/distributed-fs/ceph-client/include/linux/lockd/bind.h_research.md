<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockd/bind.h -->
# sources/distributed-fs/ceph-client/include/linux/lockd/bind.h

## Purpose
This header defines the binding contract between the kernel lock manager service (`lockd`) and filesystem clients/servers such as NFS. It centralizes lockd lifecycle and callback entry points.

## Important APIs, Types, and Functions
The file declares lockd-facing structures and operations for starting/stopping lockd, binding protocol operations, and notifying or recovering file locks. It includes service-related prototypes and callback hooks used by NFS lock management code.

## Control Flow
Callers bind lockd support, request lockd startup when network file locking is needed, and release it when no longer required. Lock recovery and grace-period callbacks flow through the declared operation hooks.

## State and Persistence Behavior
The header owns no state. Runtime state is held by lockd, NFS client/server structures, network namespaces, and file-lock tables. Persistent behavior is external, for example recovery after server reboot.

## Dependencies and Integration Points
It integrates with `fs/lockd`, NFS, `struct file_lock`, network namespaces, RPC services, and kernel lock manager recovery code.

## Risks and Test Signals
Risks include lockd lifetime imbalance, missed recovery notifications, namespace leaks, and mismatched callback versions. Test signals are NFS lock/unlock tests, lockd module unload/load, server reboot grace-period tests, and rpcdebug traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockd/bind.h -->
