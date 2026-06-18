# sources/distributed-fs/ceph-client/fs/cachefiles/xattr.c

## Purpose
`xattr.c` stores and validates CacheFiles coherency metadata in backing filesystem extended attributes for both object files and volume directories.

## Important APIs, Types, and Functions
Important types are packed `struct cachefiles_xattr` and `struct cachefiles_vol_xattr`. Public functions are `cachefiles_set_object_xattr`, `cachefiles_check_auxdata`, `cachefiles_remove_object_xattr`, `cachefiles_prepare_to_write`, `cachefiles_set_volume_xattr`, and `cachefiles_check_volume_xattr`. The xattr name is `user.CacheFiles.cache`.

## Control Flow
Setting an object xattr allocates a buffer containing object size, zero point, object type, content state, and netfs aux data, then writes it under mount write access. Checking object auxdata reads exactly the expected size and compares type, aux data, object size, and dirty content state. Dirty objects are rejected as stale pending future conflict resolution. Removing an xattr marks an object stale and treats missing xattrs as success. Volume xattr set/check writes a reserved zero field plus volume coherency bytes and validates reserved/data fields.

## State and Persistence Behavior
Object xattrs are persistent coherency records controlling whether a cache file can be reused after remount or lookup. `CACHEFILES_CONTENT_DIRTY` is written when local-write state exists. Volume xattrs persist netfs volume coherency data. Removal makes an object effectively stale.

## Dependencies and Integration Points
This file depends on VFS xattr APIs, mount write accounting, FS-Cache cookie aux/coherency accessors, CacheFiles content enums, tracepoints, and fatal I/O error handling. It is used by object lookup, commit, invalidation, volume acquisition, volume withdrawal, and write preparation.

## Risks and Edge Cases
The packed xattr layout is on-disk ABI. Exact length matching means aux length changes intentionally stale old cache files. Dirty content is currently rejected rather than reconciled. Failed xattr writes may mark the whole cache dead except for memory errors. The trace helper reads the first aux bytes as big-endian data, so zero-length aux data deserves care.

## Test Signals
Test coherent and stale object xattrs, aux mismatch, object size mismatch, dirty content rejection, missing xattr removal, EIO on get/set/remove, volume coherency mismatch, xattr length changes, and remount reuse of valid cache entries.
