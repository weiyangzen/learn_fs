# sources/distributed-fs/ceph-client/include/linux/folio_batch.h

## Purpose
This header defines a compact fixed-size batch of folio pointers used to amortize page-cache and memory-management operations.

## APIs, types, and control flow
`FOLIO_BATCH_SIZE` is 31, leaving room for the header while keeping the object power-of-two aligned. `struct folio_batch` stores count `nr`, iterator index `i`, a `percpu_pvec_drained` flag, and the folio array. `folio_batch_init()` resets all counters and drain flag; `folio_batch_reinit()` resets count/index only. Helpers report count and free space. `folio_batch_add()` appends without internal bounds checking and returns remaining slots. `folio_batch_next()` consumes entries in insertion order. `folio_batch_release()` calls `__folio_batch_release()` only when non-empty, and `folio_batch_remove_exceptionals()` removes exceptional entries.

## State and dependencies
State is caller-owned stack or heap storage. The batch does not own folios semantically but release helpers may drop references as implemented elsewhere.

## Integration, risks, and tests
Callers include page cache, LRU, delete, and writeback paths. Risks include overfilling when callers ignore returned space, reusing without reinit, ordering bugs for operations where order matters, and mixing exceptional entries without cleanup. Tests should cover init/reinit, add capacity, iteration exhaustion, release on empty/non-empty batches, and exceptional-entry removal.
