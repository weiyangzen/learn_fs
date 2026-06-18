<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaConfig.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaConfig.h

Purpose: Defines common quota request configuration shared by derived quota retrieval configs.

Important APIs/types: `QuotaConfig` stores quota data type (`cfgType`), limit type (`cfgLimitType`), list-selection mode (`cfgUseAll`), and an ID list pointer (`cfgIDList`). Defaults select user data, size+inode limits, all IDs, and no explicit list.

Control flow/state/persistence: Plain data structure. It does not own the `UIntList*`, so list lifetime is managed by callers.

Dependencies/integration: Includes `QuotaData.h`. Extended by `GetQuotaInfoConfig` and used by quota messages/workers.

Risks/test signals: Pointer ownership and null handling are the main hazards. Tests should cover explicit ID list mode, all-ID mode, user/group modes, and derived config copying.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaConfig.h -->
