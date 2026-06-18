# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/thread-utils.h

## Purpose
`thread-utils.h` declares VDO thread lifecycle helpers.

## Important APIs, Types, And Functions
It forward-declares `struct thread` and exposes `vdo_initialize_threads_mutex()`, `vdo_create_thread()`, and `vdo_join_threads()`. `vdo_create_thread()` takes a `void (*)(void *)` function, data pointer, name, and output wrapper pointer.

## Control Flow
The header defines the lifecycle contract: initialize the mutex, create a named thread, and later join it using the returned wrapper.

## State And Persistence
There is no persistent state. Runtime state is owned by the implementation's wrapper and global list.

## Dependencies And Integration Points
The header includes Linux atomic definitions and is included by code that needs to spawn VDO-managed kernel threads.

## Risks
The opaque `struct thread` prevents direct caller cleanup, so callers must use `vdo_join_threads()` exactly once after a successful create. Return values can be VDO allocation errors or kernel `PTR_ERR()` values.

## Test Signals
Compile and runtime tests should validate lifecycle pairing, error propagation, and caller inability to depend on wrapper internals.
