# sources/distributed-fs/openafs/src/afs/OBSD/osi_misc.c

## Purpose
Miscellaneous OpenBSD OSI helpers for superuser checks, kernel allocation, and unsupported inode syscalls.

## Important APIs, Types, and Functions
Defines `afs_osi_suser`, `osi_obsd_Alloc`, `osi_obsd_Free`, and stubs `afs_syscall_icreate`, `afs_syscall_iopen`, `afs_syscall_iincdec` returning `EINVAL`.

## Control Flow
`afs_osi_suser` wraps OpenBSD `suser`/`suser_ucred` and normalizes success to true. Allocators choose `malloc/free` or legacy `MALLOC/FREE` depending on OpenBSD version. Sleeping allocations drop `AFS_GLOCK` if currently held, then reacquire it.

## State and Persistence
No owned persistent state. Allocation uses kernel heap type `M_AFSGENERIC`. Inode syscall stubs do not modify state.

## Dependencies and Integration Points
Used by `osi_machdep.h` macros for `AFS_KALLOC` and privilege checks. Depends on OpenBSD malloc APIs and process accounting fields.

## Risks
Dropping GLOCK around allocation allows concurrent AFS state changes, so callers must tolerate that. The `afs_suser` macro in the header always checks current credentials, not necessarily the passed credential. Inode syscall stubs mean server/salvager inode operations are unsupported on this platform.

## Test Signals
Privilege tests for root/non-root callers, allocation tests under held and unheld GLOCK, build checks for both legacy and newer OpenBSD allocation APIs, and explicit tests that inode syscalls fail cleanly with `EINVAL`.
