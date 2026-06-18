# sources/distributed-fs/ceph-client/fs/cachefiles/volume.c

## Purpose
`volume.c` maps FS-Cache volume cookies to CacheFiles backing directories and fanout subdirectories.

## Important APIs, Types, and Functions
The public functions are `cachefiles_acquire_volume`, `cachefiles_free_volume`, and `cachefiles_withdraw_volume`. The internal `__cachefiles_free_volume` releases dentries and clears the FS-Cache private pointer.

## Control Flow
Acquire allocates `struct cachefiles_volume`, builds a directory name from the volume key prefixed with `I`, enters cache credentials, creates or opens the volume directory, sets or validates its xattr coherency data, replaces stale volume directories by burying them, then creates and pins 256 fanout directories named `@00` through `@ff`. On success it stores the volume in `vcookie->cache_priv`, increments `n_accesses` to pin wakeups, and links the volume into the cache list. Free removes the volume from the cache list and releases fanout and volume dentries. Withdraw updates the volume xattr before freeing.

## State and Persistence Behavior
Persistent state is the volume directory, its coherency xattr, and the 256 fanout directories containing object files. Runtime state is the `cachefiles_volume` with `dentry`, `fanout[]`, `vcookie`, cache link, and cache pointer.

## Dependencies and Integration Points
This file uses `cachefiles_get_directory`, `cachefiles_put_directory`, xattr coherency helpers, FS-Cache volume access accounting, cache object-list lock, and namei burial for stale volume directories.

## Risks and Edge Cases
Partial fanout creation must unwind all directories. Coherency mismatches must remove stale directories without leaving active marks. The fixed 256-way fanout is part of object path layout and must match object lookup by low cookie hash byte.

## Test Signals
Test new volume creation, existing coherent volume reuse, stale volume xattr replacement, fanout creation failure unwind, concurrent volume withdraw/free, and object lookup across all fanout buckets.
