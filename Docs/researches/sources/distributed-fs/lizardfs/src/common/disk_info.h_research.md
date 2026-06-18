# sources/distributed-fs/lizardfs/src/common/disk_info.h

Purpose: declares disk and HDD statistics structures for serialization and runtime atomic collection.

Important APIs/types/functions: `HddAtomicStatistics` stores atomic byte/time/op/max counters with `clear()`. `HddStatistics` is a serializable non-atomic snapshot with `clear()` and `add()`. `DiskInfo` serializes disk entry size, path, flags, last error chunk/time, space usage, chunk count, and minute/hour/day stats. Flags include delete, damaged, and scan-in-progress masks.

Control flow: atomic stats are reset by assigning zero to each atomic. Serializable macros generate snapshot fields and likely serialization functions.

State and persistence: `DiskInfo` and `HddStatistics` are persistence/protocol records. `HddAtomicStatistics` is runtime state intended for concurrent counters but max updates are just assignments in clear, not compare-exchange update helpers.

Dependencies and integration: depends on `MooseFsString` and `serialization_macros.h`. Used by chunkserver/master status and admin interfaces.

Risks: consumers must safely snapshot atomics into `HddStatistics`; this file does not provide that conversion. Flag masks are constants but there are no typed helpers enforcing valid combinations.

Test signals: no direct tests in subset.
