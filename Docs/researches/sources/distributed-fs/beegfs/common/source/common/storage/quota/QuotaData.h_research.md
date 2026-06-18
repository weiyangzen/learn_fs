<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaData.h -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaData.h

Purpose: Defines quota usage data, quota maps, quota enums, and serialization traits.

Important APIs/types: Aliases include `QuotaDataMap`, `QuotaDataMapForTarget`, and `QuotaDataList`. Enums cover data type, limit type, and exceeded-error type. `SessionQuotaInfo` stores per-session quota counters. `QuotaData` stores ID, size, inode count, type, and validity with merge helpers, list insertion helper, string conversion helpers, and static persistence/formatting methods.

Control flow/state/persistence: `QuotaData::serialize` writes ID, size, inodes, type, and validity. `mergeQuotaDataCounter` only merges compatible valid records; `forceMergeQuotaDataCounter` unconditionally increments counters. Map/list serialization length traits tune wire/file encoding.

Dependencies/integration: Used by quota messages, storage scans, management limits, exceeded-quota stores, and persistence helpers.

Risks/test signals: Type/validity gates must be tested because invalid quota data can poison aggregate results. Verify enum string helpers, unique list insertion, overflow behavior for counter accumulation, and map serialization compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaData.h -->
