# sources/distributed-fs/ceph-client/tools/perf/util/rwsem.h

## Purpose

`sources/distributed-fs/ceph-client/tools/perf/util/rwsem.h` declares perf's userspace read/write semaphore abstraction and lock-analysis annotations.

## Important APIs, Types, and Functions

`struct rw_semaphore` contains either a `struct mutex` in `RWS_ERRORCHECK` mode or a `pthread_rwlock_t` in normal mode. Declared APIs are init/exit and read/write down/up operations. Annotation macros mark shared, exclusive, and unlock functions.

## Control Flow

The header has no runtime flow beyond compile-time selection of the backing lock type.

## State and Persistence Behavior

The semaphore is caller-owned in-memory synchronization state.

## Dependencies and Integration Points

It includes pthread and perf mutex support. The annotations integrate with thread-safety analysis where available.

## Risks and Edge Cases

Changing `RWS_ERRORCHECK` changes semantics and performance. Consumers must initialize before use and destroy after all users have released the lock.

## Test Signals

Compile checks for both backing modes and runtime locking tests through `rwsem.c` validate the contract.
