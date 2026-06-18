# sources/distributed-fs/eos/mgm/proc/admin/NsCmd.cc

## Purpose
`NsCmd.cc` implements the protobuf-backed `ns` administrative command for the EOS MGM. It covers namespace statistics, HA status reporting, namespace tree and quota recomputation, cache management, drain/tracker/behavior controls, id reservation, and a built-in namespace performance benchmark.

## Important APIs, Types, And Functions
`NsCmd::ProcessRequest()` dispatches `NsProto` subcommands to private handlers declared in `NsCmd.hh`. Local helpers collect and format HA status: `HaClusterStatus`, `ParseRaftInfoReply()`, `CollectQdbHaStatus()`, and `BuildMgmHaStatus()`. High-impact handlers include `StatSubcmd()`, `TreeSizeSubcmd()`, `QuotaSizeSubcmd()`, `UpdateTreeSize()`, `CacheSubcmd()`, `DrainSubcmd()`, `ReserveIdsSubCmd()`, `BenchmarkSubCmd()`, `TrackerSubCmd()`, `BehaviourSubCmd()`, and `TextHighlight()`.

## Control Flow
The command first branches by protobuf oneof case. `StatSubcmd()` gathers counters from namespace services, process memory/stat/fd helpers, MGM master state, QDB raft status, FuseX client stats, cache stats, lock latency, drain/fsck/converter/balancer/tape-GC engines, and optional per-command counters. It emits either monitoring key-value output, human text with optional color highlighting, or JSON through `ResponseToJsonString()`. `TreeSizeSubcmd()` resolves a container, builds breadth-first container levels, then updates from leaves upward. `QuotaSizeSubcmd()` validates a quota node under a read lock, optionally recomputes quota core from QDB, then applies updates under a namespace write lock. `BenchmarkSubCmd()` runs mkdir/create/exist/read/write/delete phases with worker threads and root identity.

## State, Persistence, And Dependencies
This file mutates persistent namespace metadata through directory service `updateStore()`, quota node core replacement/update, namespace cache configuration, config engine cache values, id blacklisting, drain engine config, tracker state, and behavior config. It depends on global `gOFS`, `FsView`, namespace services, QuarkDB/qclient, quota, config, drain, fsck, converter, tape GC, monitoring, FuseX, and OS inspection helpers. Locks include `gOFS->eosViewRWMutex`, instrumented RWMutex controls, and internal service locks.

## Integration Points
The command is part of the asynchronous `IProcCommand` admin path and maps console protobuf requests to MGM services. Its stats output is consumed by monitoring and operational tooling. QDB HA parsing integrates namespace backend details into `ns stat`. FuseX refreshes are triggered after tree-size mutation.

## Risks
Several operations are invasive: tree and quota recomputation can traverse or rewrite large namespace regions, benchmark creates and deletes live namespace entries, and cache drops can affect latency. `QuotaSizeSubcmd()` uses `strtoul()` on uid/gid strings without rich validation. `BreadthFirstSearchContainers()` preallocates 256 levels and silently notices deeper hierarchies. `MutexSubcmd()` exists only under `EOS_INSTRUMENTED_RWMUTEX`, so behavior differs by build. The benchmark allocates raw `XrdMgmOfsFile` objects and ignores most per-file errors.

## Test Signals
Useful signals include `ns stat` in human, monitoring, summary, and JSON modes; QDB-backed and in-memory namespace modes; tree-size recomputation on nested directories; quota recomputation and partial uid/gid updates; cache drop/set commands; root-gated mutex controls in instrumented builds; benchmark cleanup after failure; and regression checks for HA fields `ns.mgm.*` and `ns.qdb.*`.
