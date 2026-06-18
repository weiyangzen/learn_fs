# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-registry.h

## Purpose
`thread-registry.h` defines the generic current-thread-to-pointer registry interface.

## Important APIs, Types, And Functions
`struct thread_registry` contains the RCU list head and spinlock. `struct registered_thread` contains the list link, stored pointer, and `task_struct *`. The header declares initialize, register, unregister, and lookup functions.

## Control Flow
The intended lifecycle is initialize registry, register a caller-owned `registered_thread` for the current task, use lookups from code running on that task, and unregister before the task or pointed-to data disappears.

## State And Persistence
Registry state is volatile kernel memory. Nothing is persisted or encoded.

## Dependencies And Integration Points
It includes Linux list and spinlock definitions and is included by specialized registries such as `thread-device.h`.

## Risks
Because nodes are caller-owned, the header contract requires stable storage until after unregister and RCU grace handling in the implementation. It also keys only by `current`, so it is unsuitable for looking up arbitrary tasks.

## Test Signals
Tests should verify structure initialization, include dependencies, lifecycle pairing, and integration with wrappers that store typed pointers.
