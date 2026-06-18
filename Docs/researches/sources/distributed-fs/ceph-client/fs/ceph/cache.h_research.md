# sources/distributed-fs/ceph-client/fs/ceph/cache.h

## Purpose

`cache.h` declares the CephFS fscache interface and provides compile-time fallbacks when `CONFIG_CEPH_FSCACHE` is disabled. It keeps the rest of the Ceph client code able to call cache helpers unconditionally while mapping those calls either to real fscache/netfs operations or to no-op/filemap behavior.

## Important APIs and Types

With `CONFIG_CEPH_FSCACHE`, the header declares the implementation functions from `cache.c`: filesystem volume registration, inode cookie registration, cookie use/unuse, cookie update, and invalidation. It also defines `ceph_fscache_cookie`, `ceph_fscache_resize`, `ceph_fscache_unpin_writeback`, `ceph_fscache_dirty_folio`, and `ceph_is_cache_enabled`.

Without fscache support, the same names are provided as static inline no-ops or simple fallbacks. `ceph_fscache_dirty_folio` becomes `filemap_dirty_folio`, `ceph_fscache_cookie` returns `NULL`, `ceph_fscache_unpin_writeback` returns success, and `ceph_is_cache_enabled` returns false.

## Control Flow

The header’s control flow is entirely compile-time. Code in `addr.c`, mount setup, and inode teardown can call the Ceph fscache API without surrounding every callsite with preprocessor checks. When enabled, dirty folio handling goes through netfs/fscache dirty tracking; when disabled, it uses normal filemap dirtying.

## State and Persistence Behavior

When enabled, the inline helpers expose the fscache cookie stored in `ci->netfs` and allow cache resize operations to be bracketed by cookie use/unuse calls. When disabled, no cache state is stored or persisted and all state-changing helpers are empty.

## Dependencies and Integration Points

The header depends on `<linux/netfs.h>` unconditionally and `<linux/fscache.h>` when enabled. It integrates directly with `struct ceph_inode_info`, `struct ceph_fs_client`, VFS `inode`, `fs_context`, and writeback-control paths. `addr.c` relies on the macro/function compatibility layer to keep writeback and invalidation code simple.

## Risks and Edge Cases

The main risk is semantic divergence between enabled and disabled builds. In enabled builds, dirty-folio behavior uses netfs, private-2 writeback pinning, and cookie coherency; disabled builds bypass all of that. The resize helper must use/unuse the cookie only when a cookie exists. Function signatures in both branches must remain synchronized or build coverage will differ by config.

## Test Signals

Build and boot-test both `CONFIG_CEPH_FSCACHE=y` and disabled configurations. Check that buffered writes mark dirty folios correctly in both modes, cache resize/invalidate callsites compile without ifdefs, and no fscache symbols are referenced in disabled builds. Runtime tests should verify `ceph_is_cache_enabled` follows cookie state only in enabled builds.
