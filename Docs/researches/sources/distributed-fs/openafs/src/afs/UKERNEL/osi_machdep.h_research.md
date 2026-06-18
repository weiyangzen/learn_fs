# sources/distributed-fs/openafs/src/afs/UKERNEL/osi_machdep.h

## Purpose

`osi_machdep.h` defines UKERNEL-specific OSI machine dependencies. It maps OpenAFS kernel abstractions to user-space types, locks, time functions, lookup helpers, and current-user accessors.

## Important APIs, Types, and Functions

It sets constants such as `MAX_OSI_PATH`, `MAX_OSI_FILES`, `MAX_OSI_LINKS`, `OSI_WAITHASH_SIZE`, and `MAX_HOSTADDR`. It maps `afs_ucred_t` to `struct usr_ucred`, `afs_proc_t` to `struct usr_proc`, and `AFS_KALLOC` to `afs_osi_Alloc`.

It defines time helpers `afs_hz`, `osi_Time`, and inline `osi_GetTime`; lookup macros `gop_lookupname` and `gop_lookupname_user`; global-lock declarations and macros `ISAFS_GLOCK`, `AFS_GLOCK`, `AFS_GUNLOCK`, `AFS_ASSERT_GLOCK`; current user macros `setuerror`, `getuerror`, and `osi_curcred`; and `osi_procname`.

## Control Flow

The lock macros are the only executable behavior: `AFS_GLOCK` enters `afs_global_lock` and records the pthread owner; `AFS_GUNLOCK` asserts ownership, clears the owner, and exits the mutex. `osi_GetTime` calls `gettimeofday` and copies seconds/useconds into OpenAFS's 32-bit timeval type.

## State and Persistence Behavior

The header declares `afs_global_owner`, `afs_global_lock`, and `afs_bufferpages`, but does not define them. It relies on thread-local `get_user_struct()` state for current credentials and user error storage.

## Dependencies and Integration Points

It is included through `afs_osi.h` in the UKERNEL build. It is foundational for all UKERNEL files and must match implementations in `afs_usrops.c` and definitions in `sysincludes.h`.

## Risks and Edge Cases

The global-lock owner is a `pthread_t` compared by `==` and cleared with `memset`; that assumes the platform's pthread type tolerates those operations. `osi_Time` has second granularity. `osi_procname` always returns `"(unknown)"`, so diagnostics lose process names in UKERNEL.

## Test Signals

Build and runtime tests should assert that nested lock misuse panics, current credential macros return per-thread credentials, path lookup macros reach `lookupname`, and `osi_GetTime` produces sane wall-clock values.
