# sources/distributed-fs/beegfs-go/ctl/pkg/ctl/stats/rebalancing.go

## Purpose
Retrieves chunk-balance job statistics from metadata or storage nodes, used to observe rebalancing work.

## Important APIs, Types, And Functions
Exports `ChunkBalanceNodeStatus`, `ChunkBalanceStatusForNodes`, and `ChunkBalanceStatusForNode`. Internal helper `chunkBalanceStatusForNode` sends the BeeMsg request.

## Control Flow
The multi-node function gets a node store and filtered node list, then queries each node sequentially. The single-node function resolves one node by entity ID. The helper rejects non-meta/non-storage node types, sends `GetChunkBalanceJobStatsMsg`, wraps transport errors with a version-support hint, and returns the node, stats response, and per-node error field.

## State And Persistence
No local state or mutations. It reads active server-side rebalancing stats.

## Dependencies And Integration Points
Depends on `config.NodeStore`, shared `getNodeList`, BeeMsg chunk-balance stats messages, and common BeeGFS node types.

## Risks And Edge Cases
`ChunkBalanceStatusForNodes` aborts on helper errors that are returned as hard errors, but transport errors are embedded in `ChunkBalanceNodeStatus.Err`; consumers must inspect both function error and per-node error. Multi-node queries are sequential, unlike other stats collection.

## Test Signals
No direct tests. Coverage should verify node-type rejection, version-hint wrapping, and per-node error propagation.
