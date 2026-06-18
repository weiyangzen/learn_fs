<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/quota/SetExceededQuotaMsgEx.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/quota/SetExceededQuotaMsgEx.cpp

## Purpose
Receives quota-exceeded state from management and updates metadata-server exceeded-quota stores for all targets in a storage pool.

## Important APIs, Types, and Functions
`processIncoming()` checks `QuotaEnableEnforcement`, resolves the requested `StoragePool`, iterates pool targets, retrieves each `ExceededQuotaStore`, calls `updateExceededQuota(getExceededQuotaIDs(), getQuotaDataType(), getExceededType())`, and sends `SetExceededQuotaRespMsg`.

## Control Flow, State, and Persistence
The operation mutates in-memory quota-exceeded state per target. It returns `UNKNOWNPOOL` for missing pools, `UNKNOWNTARGET` for missing exceeded-quota stores, and `INTERNAL` when local quota enforcement is disabled while the sender expects it.

## Dependencies and Integration Points
Depends on app config, `StoragePoolStore`, `StoragePool`, `ExceededQuotaStores`, quota data types, logging, and the quota response message. Lookup/create paths consult these stores for enforcement.

## Risks and Test Signals
Risks include config skew between management and metadata daemons, partial updates across targets when one store is missing, and stale quota state after pool membership changes. Tests should cover disabled enforcement, missing pool, missing target store, user/group quota IDs, and pool with multiple targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/quota/SetExceededQuotaMsgEx.cpp -->
