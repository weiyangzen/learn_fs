<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_utils.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_utils.cpp

Purpose: Maintains a cached copy of the server partition table and provides simple lookup helpers.

Important APIs/functions: `ReadPartitionTable` calls `cfg_HostPartitionTableEnumerate` into static `pTable`/`cPartitions`. `GetPartitionTable`, `GetNumPartitions`, `IsAnAfsPartition`, `DoesPartitionExist`, and `FreePartitionTable` expose and clear the cache.

Control flow: Readers must call `ReadPartitionTable` before lookup. `ReadPartitionTable` frees the previous table first, then replaces the cache. `FreePartitionTable` deallocates with `cfg_PartitionListDeallocate`.

State and persistence: Static process cache only. Durable partition table state lives in the cfg library/server registry and is read/written elsewhere.

Dependencies and integration points: Requires `g_hServer`, OpenAFS cfg admin APIs, TCHAR conversion helpers, and is used by current-config discovery, wizard partition selection, partition creation, and partition listing.

Risks: Global cache is not thread-safe. `DoesPartitionExist` compares ANSI partition names converted to TCHAR against caller strings, so callers must agree on `/vicepX` vs suffix naming. On failed enumerate the cache is empty even if prior data existed.

Test signals: Test enumerate success/failure, cache replacement, free idempotence, case-insensitive drive lookup, partition-name lookup with full `/vicep` names, and concurrent refresh/list usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/partition_utils.cpp -->
