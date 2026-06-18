## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_pool.c

### Purpose
`sparx5_pool.c` provides a small reference-counted ID pool used by PSFP stream filters, stream gates, and flow meters. It maps one-based external IDs to zero-based array entries.

### Important APIs, Types, And Functions
The file exports `sparx5_pool_idx_to_id()`, `sparx5_pool_put()`, `sparx5_pool_get()`, and `sparx5_pool_get_with_idx()`. It operates on arrays of `struct sparx5_pool_entry`, whose fields include `ref_cnt` and a caller-defined `idx`.

### Control Flow
`sparx5_pool_get()` returns the first unused entry and increments its reference count. `sparx5_pool_get_with_idx()` prefers an existing entry with matching `idx` and positive reference count, otherwise remembers the first free entry, stores `idx`, and increments its reference count. `sparx5_pool_put()` rejects zero references and decrements the count.

### State, Persistence, And Dependencies
Pool state is in static arrays owned by users such as `sparx5_psfp.c`; this file only manipulates counters and indices. There is no locking, persistence, or hardware access.

### Integration Points
PSFP uses the generic pool to share stream gates and flow meters for identical TC hardware indices and to allocate unique stream filters. One-based IDs match hardware conventions used by PSFP lookup helpers.

### Risks
The `size` argument is not bounds-checked against an incoming ID in `sparx5_pool_put()`, so callers must pass valid IDs. No lock protects shared static pools. `idx` remains stale after refcount reaches zero until reused, which is fine for current matching because refcount must be positive.

### Test Signals
Test first-free allocation, one-based ID conversion, reference increments for repeated `idx`, decrement-to-zero behavior, invalid put on free entries, and exhaustion behavior.
