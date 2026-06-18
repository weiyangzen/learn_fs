# sources/distributed-fs/openafs/src/afs/DARWIN/osi_prototypes.h

## Purpose
Declares Darwin-specific OSI support routines used across OpenAFS platform files.

## Important APIs, Types, And Functions
The header declares `darwin_notify_perms`, lookup helpers, `afs_suser`, VFS context get/put, signal-mask helpers, VM helpers, and Darwin vnode creation/finalization helpers.

## Control Flow
There is no executable flow. It provides compile-time contracts between `osi_misc.c`, `osi_sleep.c`, `osi_vm.c`, `osi_vnodeops.c`, and generic OpenAFS code.

## State And Persistence
No state is allocated here; declarations expose routines that manage vcache, vnode, UBC, and VFS-context state elsewhere.

## Dependencies And Integration Points
Depends on Darwin kernel types such as `user_addr_t`, `uio_seg`, `vnode`, `vcache`, and `componentname`. It is the include boundary for Darwin-only helpers.

## Risks
Prototype drift would cause ABI mismatches, especially for `afs_darwin_finalizevnode` and cdev/syscall-adjacent helpers. Conditional availability must match implementation guards.

## Test Signals
Full Darwin builds with warnings enabled are the primary signal; link failures would reveal missing or mismatched support routines.
