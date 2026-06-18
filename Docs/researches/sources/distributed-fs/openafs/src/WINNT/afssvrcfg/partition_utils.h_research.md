<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_utils.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_utils.h

Purpose: Declares partition-table cache and lookup helpers.

Important APIs/functions: `ReadPartitionTable`, `GetPartitionTable`, `GetNumPartitions`, `IsAnAfsPartition`, `DoesPartitionExist`, and `FreePartitionTable`.

Control flow: No implementation logic; callers are responsible for refreshing the cache before use.

State and persistence: Implementation maintains a static cache and reads server partition-table state.

Dependencies and integration points: Requires OpenAFS `cfg_partitionEntry_t`, `afs_status_t`, and Win32/TCHAR types via `afscfg.h`.

Risks: The API returns a raw pointer to static cached storage that becomes invalid after `ReadPartitionTable` or `FreePartitionTable`.

Test signals: Verify callers do not retain the returned pointer across refresh/free and handle zero-entry tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_utils.h -->
