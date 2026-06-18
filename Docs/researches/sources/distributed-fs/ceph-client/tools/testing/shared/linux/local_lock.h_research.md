<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/local_lock.h -->
# sources/distributed-fs/ceph-client/tools/testing/shared/linux/local_lock.h

## Purpose

`linux/local_lock.h` provides no-op local-lock primitives for userspace tests.

## Important APIs, Types, and Functions

It defines an empty `local_lock_t`, inline `local_lock()` and `local_unlock()`, and `INIT_LOCAL_LOCK(x)`.

## Control Flow and State

No lock state is maintained. Calls have no synchronization effect.

## Dependencies and Integration Points

It supports imported kernel code that expects local locks in contexts where userspace tests either serialize differently or do not need CPU-local locking.

## Risks and Test Signals

Risks include masking concurrency bugs that require local-lock semantics. Threaded tests should use real pthread primitives where needed; successful builds validate this stub for single-process harness use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/shared/linux/local_lock.h -->
