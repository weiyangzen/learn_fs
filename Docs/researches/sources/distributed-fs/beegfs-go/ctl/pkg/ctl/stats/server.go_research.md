# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/stats/server.go

## Purpose
Fetches high-resolution server stats from metadata/storage nodes and returns single-node, per-node latest, or aggregate time-series views.

## Important APIs, Types, And Functions
Exports `NodeStats`, `Stats`, `SingleServerNode`, `MultiServerNodes`, and `MultiServerNodesAggregated`. Internal helpers include `Stats.add`, `statsFromHighResolutionStats`, `getNodeList`, and `getServerStats`.

## Control Flow
`SingleServerNode` resolves one node, reads stats, reverses them into chronological order, and returns all entries. `MultiServerNodes` starts one goroutine per node and returns the second stats entry (`stats[1]`) as the latest stable sample when available. `MultiServerNodesAggregated` starts one goroutine per node, skips the two latest samples for inaccuracy, sums entries by timestamp, sorts by timestamp, and returns aggregate series plus node count. `getServerStats` sends `GetHighResStats{LastStatTime:0}` to a node.

## State And Persistence
No persistent state. It reads server counters/time-series snapshots and aggregates them in memory.

## Dependencies And Integration Points
Depends on node store, BeeMsg high-resolution stats, and common BeeGFS node filtering. Used by stats command frontends.

## Risks And Edge Cases
`MultiServerNodesAggregated` returns `err` from outer scope when `sRes.err != nil`, but that variable may be nil; it should likely return `sRes.err`. `Stats.add` assigns `StatsTime` from the other sample, which is fine for same-timestamp aggregation but would hide mismatches if misused. `MultiServerNodes` silently returns zero-value stats for nodes with errors or fewer than two samples.

## Test Signals
No direct tests. Tests should cover aggregation error propagation, short stat slices, sorting, and timestamp summing.
