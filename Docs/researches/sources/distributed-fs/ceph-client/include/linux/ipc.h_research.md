# sources/distributed-fs/ceph-client/include/linux/ipc.h

## Purpose
`ipc.h` defines the in-kernel permission and lifetime object common to System V IPC objects such as semaphore arrays, message queues, and shared memory segments.

## Important APIs, types, and functions
The central type is `struct kern_ipc_perm`, containing a spinlock, deletion flag, ID/key, owner and creator credentials, mode bits, sequence number, LSM security pointer, rhashtable node, RCU head, and refcount.

## Control flow
There are no functions in this header. IPC implementations embed or reference this structure, lock it while mutating permissions/state, use the rhashtable node for key lookup, and rely on RCU/refcounting for safe teardown.

## State and persistence
State is runtime IPC object metadata. It persists only while the IPC object exists in an IPC namespace.

## Dependencies and integration points
It depends on spinlock types, kernel uid/gid wrappers, rhashtable storage, refcounts, RCU, and UAPI IPC constants. LSMs use the `security` pointer.

## Risks and test signals
Risks include sequence-number reuse, use-after-free across RCU/refcount paths, permission races after `deleted`, and credential namespace mistakes. Tests should cover create/remove races, key lookup, permission checks, LSM hooks, and object ID recycling.
