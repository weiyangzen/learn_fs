# sources/distributed-fs/lizardfs/src/protocol/chunkserver_list_entry.h

## Purpose
Defines the serializable chunkserver status/list entry used in newer client-master chunkserver list responses.

## Important APIs, Types, And Functions
`ChunkserverListEntry` contains version, server IP/port, used/total space, chunk count, to-delete used/total space, to-delete chunk count, error counter, and label.

## Control Flow
No executable control flow beyond generated serialization methods.

## State And Persistence Behavior
No local state. Instances represent a snapshot of chunkserver state transmitted over the protocol.

## Dependencies And Integration Points
Depends on serialization macros and is referenced by `LIZ_MATOCL_CSERV_LIST` payload documentation in `MFSCommunication.h` and likely by master/client protocol handlers.

## Risks And Edge Cases
Field order is the wire contract. The string label extends older fixed-size records; mixed-version callers must use the correct packet version.

## Test Signals
Should be covered by protocol serialization tests for chunkserver list messages and compatibility tests with older list formats.
