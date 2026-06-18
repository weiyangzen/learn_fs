# sources/distributed-fs/ceph-client/fs/coda/coda_int.h

## Purpose
`coda_int.h` provides internal Coda module declarations for filesystem registration, tunables, inode-cache lifecycle, fsync, and optional sysctl hooks.

## Important APIs, Types, And Functions
It declares `coda_fs_type`, `coda_timeout`, `coda_hard`, `coda_fake_statfs`, `coda_init_inodecache()`, `coda_destroy_inodecache()`, and `coda_fsync()`. It declares `coda_sysctl_init()`/`clean()` when `CONFIG_SYSCTL` is set and provides no-op inline stubs otherwise.

## Control Flow
There is no runtime flow in the header. It lets module init/exit and VFS operation files share internal symbols without exposing them outside Coda.

## State, Persistence, And Dependencies
The declared tunables influence Coda runtime behavior but are owned by other files. There is no persistence in this header.

## Integration Points
`psdev.c`/module init uses inode-cache and sysctl declarations; `dir.c` references `coda_fsync()` for directory file operations; sysctl compilation is isolated behind config guards.

## Risks
Optional sysctl stubs must match the real signatures. Global tunables need coherent definitions in exactly one object to avoid link or behavior drift.

## Test Signals
Build with and without `CONFIG_SYSCTL`, load/unload Coda, and verify sysctl registration plus directory/file fsync linkage.
