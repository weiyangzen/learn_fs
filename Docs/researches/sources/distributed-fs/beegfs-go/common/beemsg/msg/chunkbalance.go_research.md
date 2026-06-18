# sources/distributed-fs/beegfs-go/common/beemsg/msg/chunkbalance.go

## Purpose
`chunkbalance.go` defines BeeMsg protocol messages and response structures for starting chunk balancing and reading chunk-balance job statistics.

## APIs and Control Flow
`StartChunkBalanceMsg` contains rebalance ID type, relative path, target IDs, destination IDs, entry info, and required file event context. `Serialize` writes the ID type, path CStr, target and destination sequences, entry info, sets message feature flag bit 1 when file event exists, forces the event type to protobuf `INODE_LOCKED`, and serializes the event. Missing file event fails serialization. Response and stats messages expose `MsgId` values and serialize/deserialize fixed fields. `ChunkBalancerJobState.String` formats job states.

## State, Dependencies, and Integration
The file depends on `beegfs.OpsErr`, BeeSerde, protobuf beewatch events, and message types such as `EntryInfo` and `FileEvent` defined elsewhere. Message IDs and field order are wire-protocol state and must match BeeGFS server expectations.

## Risks and Test Signals
Serialization mutates `m.FileEvent.Type`, which may surprise callers that reuse the object. There is no nil check for `EntryInfo`. Stats deserialization order is fixed and must stay in sync with the server. No listed tests cover chunk-balance message bytes or error paths.
