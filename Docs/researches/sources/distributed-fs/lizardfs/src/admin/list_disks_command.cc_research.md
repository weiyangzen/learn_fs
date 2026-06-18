<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_disks_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/list_disks_command.cc

## Purpose
Implements `lizardfs-admin list-disks`, querying every connected chunkserver for per-disk capacity, flags, error, chunk count, and optional I/O statistics.

## Important APIs, Types, and Functions
Defines formatting helpers for yes/no flags, bandwidth, operation time/count, `printStats`, `printPorcelainStats`, `printPorcelainMode`, `printNormalMode`, and command methods. It uses `DiskInfo`, `HddStatistics`, and `MooseFSVector<DiskInfo>`.

## Control Flow, State, and Persistence
`run` obtains chunkservers via `ListChunkserversCommand::getChunkserversList`, skips disconnected entries, connects directly to each chunkserver address, sends legacy `CLTOCS_HDD_LIST_V2`, deserializes `CSTOCL_HDD_LIST_V2`, and prints disk records. Verbose mode adds last-minute/hour/day read/write/fsync counters and timing. It is read-only; state is sampled from master and chunkservers.

## Dependencies and Integration Points
Depends on master chunkserver listing, direct chunkserver protocol, `DiskInfo` flags, human-readable formatting, `timeToString`, and network address conversion.

## Risks and Test Signals
Risks include sequential direct connections to all chunkservers, partial output if one chunkserver is unreachable, no escaping for disk paths in porcelain mode, write-throughput calculation combining write and fsync time, and skipped disconnected servers hiding stale disks. Test signals are chunkserver discovery, disconnected skip, disks with to-delete/damaged/scanning flags, last-error formatting, verbose statistics, direct chunkserver timeout/error behavior, and paths containing spaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_disks_command.cc -->
