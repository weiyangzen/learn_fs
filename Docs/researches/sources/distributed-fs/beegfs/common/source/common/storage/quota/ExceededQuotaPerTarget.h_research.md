<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaPerTarget.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaPerTarget.h

Purpose: Declares a target-id indexed container for exceeded quota state.

Important APIs/types: `ExceededQuotaPerTarget` exposes `get`, `add`, and `remove`. Private state is an `RWLock` plus `std::map<uint16_t, ExceededQuotaStorePtr> exceededQuotaStores`.

Control flow/state/persistence: The header defines the ownership model: stores are shared pointers, allowing returned stores to outlive map membership. Persistence is delegated elsewhere; this object is a synchronization and registry layer.

Dependencies/integration: Includes `ExceededQuotaStore.h` and BeeGFS threading primitives. It is an integration point between target selection and quota enforcement checks.

Risks/test signals: The map key is a 16-bit target ID; invalid target handling is caller-owned. Tests should validate null returns, duplicate handling, removal semantics, and ABI expectations around `const ExceededQuotaStorePtr` return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/ExceededQuotaPerTarget.h -->
