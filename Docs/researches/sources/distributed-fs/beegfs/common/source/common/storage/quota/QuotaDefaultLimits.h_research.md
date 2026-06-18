<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaDefaultLimits.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaDefaultLimits.h

Purpose: Declares default quota limit storage for user/group inode and size limits.

Important APIs/types: `QuotaDefaultLimits` has getters, `updateUserLimits`, `updateGroupLimits`, `updateLimits`, `clearLimits`, file load/save methods, and serialization helpers. Private state includes `storePath` plus four `uint64_t` limit values.

Control flow/state/persistence: The header defines a value object with an associated persistence path. `serialize` writes user inode/size then group inode/size; `deserialize` requires the same order.

Dependencies/integration: Includes BeeGFS serialization helpers and quota logging dependencies in the implementation. Used wherever default quota policies are managed.

Risks/test signals: Field order is the persistent file format. Tests should verify updates preserve unrelated limits, serialization round trips, empty path failure behavior, and limits of zero as "unset/no default" semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaDefaultLimits.h -->
