# sources/distributed-fs/openafs/src/afs/afs_sysname.c

## Purpose

`afs_sysname.c` owns the global `@sys` expansion name list used by the AFS client. It initializes a fixed-size list of system names, defaults the first entry to `SYS_NAME`, exposes generation state through `afs_sysnamegen`, and controls behavior through `afs_atsys_type`, which defaults to `AFS_ATSYS_INTERNAL`.

## Important APIs, Types, and Functions

Global state includes `afs_global_sysnames`, `afs_sysnamegen`, `afs_sysname_lock`, and `afs_atsys_type`. The public lifecycle functions are `afs_sysname_init(void)` and `afs_sysname_shutdown(void)`. Internal helpers `sysnamelist_init` and `sysnamelist_destroy` allocate and free each `MAXSYSNAME` buffer in the `struct afs_sysnames` array, set `namecount`, and clear the structure on teardown.

## Control Flow and State

Initialization is guarded by a static `init_done`. On first call, the file initializes `afs_sysname_lock`, allocates `MAXNUMSYSNAMES` name buffers in a static `global_sysnames` object, copies `SYS_NAME` into slot zero with `strlcpy`, sets `namecount` to one, assigns `afs_global_sysnames`, increments `afs_sysnamegen`, and returns success. If allocation or default-copy fails, it calls `afs_sysname_shutdown` to clean partial state. Shutdown frees all allocated name buffers, zeros the list, clears the global pointer, and destroys the mutex.

## Dependencies and Integration Points

Consumers of `@sys` path expansion and pioctl sysname setters/readers use `afs_global_sysnames` and `afs_sysnamegen`. The file documents an important lock order: hold `afs_sysname_lock` when reading or writing the sysname list, and acquire `afs_sysname_lock` before `GLOCK` if both are required. The mutex is deliberately not an `afs_rwlock_t`, so it can be used outside `GLOCK`.

## Persistence and Side Effects

The sysname list is memory-resident kernel state. It survives for the Cache Manager runtime and can be changed by other sysname-management code, but this file only creates the default list and destroys it at shutdown. The generation counter lets consumers detect list updates.

## Risks and Test Signals

Risks include use after shutdown if consumers do not check `afs_global_sysnames`, allocation leaks on partial initialization, lock-order inversions with `GLOCK`, and truncation failures if `SYS_NAME` exceeds `MAXSYSNAME`. Test signals include startup default sysname, repeated `afs_sysname_init` idempotence, clean shutdown under leak checking, and pioctl/sysname expansion behavior after list updates.
