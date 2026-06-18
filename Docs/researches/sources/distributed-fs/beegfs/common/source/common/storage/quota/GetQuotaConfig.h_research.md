<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaConfig.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaConfig.h

Purpose: Defines the request configuration structure for quota information retrieval.

Important APIs/types: `GetQuotaInfoConfig` extends `QuotaConfig` with `cfgTargetSelection`, `cfgTargetNumID`, and `cfgIDRangeStart`, selecting whether data is requested for all targets in one request, per target, or for a single target/range.

Control flow/state/persistence: This is a plain configuration value passed to worker/message code. It has no persistence or locking behavior.

Dependencies/integration: Includes `QuotaConfig.h` and `TargetSelection.h`. It is consumed by `GetQuotaInfo`, `GetQuotaInfoWork`, and quota request messages.

Risks/test signals: Defaults select all targets in one request, target ID 0, and ID range 0. Tests should verify callers override defaults for single-target and per-target modes and that storage pool filtering is only used with compatible target-selection modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/GetQuotaConfig.h -->
