# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/sync.h

## Purpose

`sync.h` declares a Windows read/write lock abstraction for NetIDMgr utilities. It provides multiple-reader/single-writer coordination using a `CRITICAL_SECTION`, event handles, lock counters, status, and a writer thread id.

## Important APIs, types, and functions

The central type is `rw_lock_t`, also exposed as `RWLOCK` and `PRWLOCK`. It stores `locks`, `status`, `cs`, `readwx`, `writewx`, and `writer`. Lifecycle APIs are `InitializeRwLock` and `DeleteRwLock`. Locking APIs are `LockObtainRead`, `LockReleaseRead`, `LockObtainWrite`, and `LockReleaseWrite`.

## Control flow

The documented behavior is classic reader/writer arbitration. Readers can share access unless a writer owns or is pending on the lock. Writers wait until readers drain, and recursive write locks by the same thread are supported if every obtain has a matching release. Wakeups are issued to waiting readers or writers after release.

## State and persistence behavior

All state is in the caller-owned `RWLOCK` object and Windows kernel synchronization primitives created during initialization. The state is process-lifetime only and must be deleted to close handles.

## Dependencies and integration points

The header depends on `khdefs.h` and Windows types. It is included by `utils.h`, making it part of the common NetIDMgr utility surface. Shared credential/configuration code can use it where concurrent readers and exclusive writers are needed.

## Risks and edge cases

The implementation contract requires strict acquire/release pairing. Failing to call `DeleteRwLock` can leak handles. Recursive write support is documented, but recursive read behavior and upgrade/downgrade semantics are not defined here. Writer fairness depends on implementation details outside this header.

## Test signals

Tests should exercise concurrent readers, writer exclusion, release wakeups, recursive write acquire/release by one thread, deletion after use, and stress for writer starvation or missed wakeups.
