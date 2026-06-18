# sources/distributed-fs/ceph-client/fs/ceph/cache.c

## Purpose

`cache.c` implements the runtime fscache glue for CephFS. It registers an fscache volume for a mounted Ceph filesystem, acquires per-inode cache cookies for regular files, and wraps cookie use, updates, and invalidation so address-space code can cache remote file data coherently.

## Important APIs and Functions

`ceph_fscache_register_fs` builds a volume name from the cluster fsid plus optional `fscache_uniq` mount option and calls `fscache_acquire_volume`. `ceph_fscache_unregister_fs` relinquishes that volume.

`ceph_fscache_register_inode_cookie` acquires a per-inode cookie keyed by `ceph_vino`, versioned by `ci->i_version`, and sized from `i_size_read`. It only registers cookies when the mount has fscache enabled, the inode is a regular file, and the inode is new. `ceph_fscache_unregister_inode_cookie` relinquishes the cookie.

`ceph_fscache_use_cookie` and `ceph_fscache_unuse_cookie` bracket modifications or read/write activity; the update path passes the current inode version and size back to fscache. `ceph_fscache_update` updates cookie coherency metadata. `ceph_fscache_invalidate` invalidates cached contents and marks direct-I/O invalidations with `FSCACHE_INVAL_DIO_WRITE`.

## Control Flow

Mount setup calls `ceph_fscache_register_fs`; failures are reported through `errorfc` and leave `fsc->fscache` null so later inode registration is skipped. New regular inodes call `ceph_fscache_register_inode_cookie`, which stores the acquired cookie in `ci->netfs.cache` and sets `mapping_set_release_always` so release callbacks run even when pages look otherwise releasable.

Buffered writeback and cache invalidation code in `addr.c` call the cookie wrappers. When `update` is true during unuse, the cookie receives both `i_version` and current size to keep the cache coherent with MDS-observed file changes.

## State and Persistence Behavior

The persistent external state is the local fscache backend’s volume and per-file cached data. In kernel memory, the Ceph filesystem client stores the volume cookie in `fsc->fscache`; each inode stores the netfs/fscache cookie in `ci->netfs.cache`. Cookie coherency depends on `ci->i_version` and `i_size`.

## Dependencies and Integration Points

This file depends on Linux fscache and netfs APIs, `fs_context` for mount error reporting, and Ceph inode/client helpers from `super.h`. `addr.c` uses these wrappers for dirty folios, write-to-cache, resize, invalidation, and cache-enabled checks via `cache.h`.

## Risks and Edge Cases

The code intentionally avoids caching non-regular or non-new inodes. A stale or missing `i_version` update can expose old cached data. Direct I/O invalidation must carry the direct-write flag so fscache does not trust cached pages across external writes. Registration failures degrade to no cache rather than failing the mount in all cases.

## Test Signals

Exercise mounts with and without fscache, unique fscache volume names, regular versus directory/special inode registration, cache invalidation after direct I/O, writes followed by remount/readback, and fscache backend unavailability. Useful signals are non-null `ci->netfs.cache` only for eligible files, no cache use when `fsc->fscache` is null, and correct cache invalidation/update traces under writeback.
