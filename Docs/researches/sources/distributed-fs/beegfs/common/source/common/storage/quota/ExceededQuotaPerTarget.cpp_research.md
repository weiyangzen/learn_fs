<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaPerTarget.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaPerTarget.cpp

Purpose: Implements thread-safe lookup, insertion, and removal of per-target exceeded-quota stores.

Important APIs/functions: `get(targetId)` returns a shared `ExceededQuotaStorePtr` or null. `add(targetId, ignoreExisting)` creates or returns a store depending on existing state and policy. `remove(targetId)` erases a target entry.

Control flow/state/persistence: A `RWLockGuard` protects the backing `std::map<uint16_t, ExceededQuotaStorePtr>`. Reads acquire a read lock; add/remove acquire a write lock. The class is an in-memory registry only and does not write target quota state to disk.

Dependencies/integration: Depends on `ExceededQuotaPerTarget.h`, `ExceededQuotaStore`, and BeeGFS `RWLockGuard`. Used by quota enforcement code that needs target-scoped exceeded ID sets.

Risks/test signals: The `ignoreExisting` flag controls whether duplicate add returns the existing store or null, so caller expectations should be tested. Concurrency tests should cover parallel add/get/remove and shared pointer lifetime after removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaPerTarget.cpp -->
