## sources/distributed-fs/ceph-client/include/linux/cache_coherency.h

**Purpose:** This header defines a driver-facing framework for cache coherency maintenance operation providers.

**Important APIs/types/functions:** `struct cc_inval_params` carries physical address and size. `struct cache_coherency_ops` exposes `wbinv()` and `done()` callbacks. `struct cache_coherency_ops_inst` embeds a `kref`, list node, and ops pointer. APIs include register/unregister, `_cache_coherency_ops_instance_alloc()`, typed `cache_coherency_ops_instance_alloc()`, and `cache_coherency_ops_instance_put()`.

**Control flow, state, persistence:** Providers allocate/register instances, callers invoke operations through framework code implemented elsewhere, and refs control instance lifetime. Maintenance operations affect hardware cache state but create no persistent storage.

**Dependencies/integration:** Depends on list, kref, phys address types, and `static_assert`/`offsetof` constraints. The typed allocator requires the embedded instance member to be at offset zero.

**Risks and test signals:** Risks are freeing registered instances, embedding the instance at nonzero offset, incomplete `done()` sequencing, and invalid physical ranges. Test signals include provider register/unregister, refcount leak tests, invalidation/writeback-invalidate hardware validation, and compile failures for malformed embedding.
