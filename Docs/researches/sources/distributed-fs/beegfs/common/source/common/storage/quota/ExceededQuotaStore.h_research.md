<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaStore.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaStore.h

Purpose: Declares the exceeded-quota ID set container used by quota enforcement.

Important APIs/types: `ExceededQuotaStore` exposes update, query, copy-out, and non-empty checks. Private state has four `UIntSet` members: user/group size exceeded and user/group inode exceeded. `ExceededQuotaStorePtr` is a shared pointer alias.

Control flow/state/persistence: Thread-safety is implemented in the `.cpp` with an `RWLock`. State is memory-only and expected to be refreshed from quota scans or management updates.

Dependencies/integration: Includes `QuotaData.h`, `RWLock`, and common BeeGFS collection aliases. It is often nested under `ExceededQuotaPerTarget`.

Risks/test signals: The header exposes pointer-based inputs (`UIntList*`), so null-pointer behavior is not guarded by the API. Tests should exercise all enum branches and ensure invalid enum values do not silently corrupt unrelated sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaStore.h -->
