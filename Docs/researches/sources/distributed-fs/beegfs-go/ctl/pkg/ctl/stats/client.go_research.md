# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/stats/client.go

## Purpose
Fetches, normalizes, diffs, and aggregates per-client or per-user operation counters from metadata and storage servers.

## Important APIs, Types, And Functions
Exports operation-name slices, `ClientOps`, methods `Sub`/`Add`, `Diff`, `SumAllOpsFromSingleServer`, `SingleNodeClients`, and `PerNodeType`. Internal helpers include `sumEachOpFromAllServers` and `getClientStats`.

## Control Flow
`SingleNodeClients` resolves one node and reads one stats result. `PerNodeType` gets eligible nodes, starts one stats goroutine per node, reads their results, and aggregates by client/user ID. `getClientStats` probes whether a node supports `GetClientStatsV2`, then pages through stats using a cookie until `moreData` is false. It validates minimum response size, protocol version, and record layout, normalizes old IPv4 and V2 ID byte ordering for client stats, appends operation slices, updates cookie, and sorts results.

## State And Persistence
No persistent state. It reads server counters since server start and produces snapshots or interval diffs. `Diff` and aggregation mutate copies or map values in memory.

## Dependencies And Integration Points
Depends on node store, BeeMsg request/response types for metadata/storage stats, global node filtering in `server.go`, and common BeeGFS entity types.

## Risks And Edge Cases
Several error sends in `getClientStats` do not immediately return after protocol/layout validation, so a goroutine may continue and attempt to send more results into a buffered size-one channel, risking block or confusing consumers. `PerNodeType` initializes `statsList` with length `len(nodes)` and then appends each node's stats, leaving leading nil entries that are harmless for aggregation but wasteful and misleading. The loop condition for records uses `l < len(stats)` while indexing `opsSlice`, which deserves close review for off-by-one behavior.

## Test Signals
No direct tests. Needed tests include V1/V2 normalization, multi-page cookies, malformed response sizes, protocol mismatch, aggregation, and diff behavior.
