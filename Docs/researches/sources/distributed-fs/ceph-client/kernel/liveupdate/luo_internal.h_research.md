# sources/distributed-fs/ceph-client/kernel/liveupdate/luo_internal.h

## Purpose
`luo_internal.h` defines private LUO structs and function prototypes shared between core, session, file, and FLB implementations.

## Important APIs, Types, and Functions
`struct luo_ucmd` wraps a user buffer, user-provided size, and kernel command buffer. `luo_ucmd_respond()` copies the smaller of user and kernel struct sizes back to userspace. `luo_restore_fail()` panics on unrecoverable restore failures.

`struct luo_file_set` groups a list of preserved files, preserved serialization memory, and count. `struct luo_session` stores name, serialized pointer, list node, retrieval flag, file set, and mutex. The header declares session, file, and FLB internal APIs plus `extern struct rw_semaphore luo_register_rwlock`.

## Control Flow
Core ioctl handlers and session ioctl handlers use `luo_ucmd` for ABI-size-compatible command handling. Session code calls file-set APIs. File code calls FLB APIs. Early and late init call setup functions for incoming/outgoing session and FLB FDT nodes.

## State and Persistence Behavior
The header defines the runtime containers whose contents are serialized through KHO by the corresponding `.c` files. The panic macro encodes the policy that failed incoming deserialization is not recoverable.

## Dependencies and Integration Points
It includes public `<linux/liveupdate.h>` and user access helpers. It is included by every LUO implementation file and connects to UAPI structs defined in liveupdate ABI headers.

## Risks and Test Signals
`luo_ucmd_respond()` must not leak beyond the user's advertised size and must handle short new/old ABI structs. The panic policy should be validated in restore-failure tests. Structure invariants include initialized file-set lists, session mutexes, and zero counts on destroy.
