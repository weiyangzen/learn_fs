<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaData.cpp -->
## sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaData.cpp

Purpose: Implements serialization-file persistence and human-readable formatting for quota maps/lists.

Important APIs/functions: `loadQuotaDataMapForTargetFromFile` reads a serialized `QuotaDataMapForTarget`. `saveQuotaDataMapForTargetToFile` creates parent directories and writes serialized map data. `quotaDataMapToString`, `quotaDataMapForTargetToString`, and `quotaDataListToString` format usage values.

Control flow/state/persistence: Loading opens, stats, allocates a full-file buffer, reads once, and deserializes. Saving serializes into a new buffer then creates/truncates/writes the target file. There is no temporary-file atomic rename, so partial writes or crashes can leave corrupt state.

Dependencies/integration: Uses BeeGFS `Serialization`, `StorageTk`, `Path`, logging, POSIX `open/read/write/stat`, and quota collection aliases.

Risks/test signals: Tests should cover missing/empty/corrupt files, partial read/write behavior, large maps, directory creation failures, serialization round trips, and debug counter paths. Persistence tests should note truncate-write crash risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/storage/quota/QuotaData.cpp -->
