# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/Sender.java

## Purpose
`Sender` is the client-side serializer for `DataTransferProtocol`. Each method writes the data transfer version, operation code, and operation-specific protobuf to a `DataOutputStream`, then flushes.

## Important APIs, Types, and Functions
`op` writes `DATA_TRANSFER_VERSION` followed by the `Op` byte. `send` logs, writes the op, writes a delimited protobuf, and flushes. `getCachingStrategy` converts optional readahead/drop-behind fields into `CachingStrategyProto`.

Protocol methods build the corresponding protobufs: `OpReadBlockProto`, `OpWriteBlockProto`, `OpTransferBlockProto`, short-circuit request protos, `OpReplaceBlockProto`, `OpCopyBlockProto`, `OpBlockChecksumProto`, and `OpBlockGroupChecksumProto`. `writeBlock` converts target arrays with offsets because the receiver DataNode is not included in downstream target arrays. `releaseShortCircuitFds` and `requestShortCircuitShm` attach tracing context when present. `blockGroupChecksum` serializes striped block datanodes, tokens, indices, EC policy, requested bytes, and checksum options.

## Control Flow
Every public method follows build-protobuf then `send`. Optional fields such as source DataNode, storage ID, slot ID, and tracing info are set only when non-null or present.

## State and Persistence Behavior
The only instance state is the output stream. Wire state is the version/op/protobuf sequence. No local persistence.

## Dependencies and Integration Points
It depends on DataTransfer protobufs, `DataTransferProtoUtil`, `PBHelperClient`, HDFS block/datanode/storage/checksum types, `CachingStrategy`, block tokens, tracing utilities, and `Op`. It is used by DFS client/DataNode/balancer code to initiate operations against a DataNode.

## Risks and Edge Cases
Sender and receiver protobuf schemas must stay in lockstep. Array conversions with offset `1` must align with pipeline semantics. `targetStorageIds` is converted with `Arrays.asList` in `transferBlock`, so null arrays would fail. Flushing every op is required for handshake/protocol progress but affects buffering behavior.

## Test Signals
`TestDataTransferProtocol`, DataNode backward compatibility tests, short-circuit tests, and EC checksum tests cover serialized operations. Focused tests should inspect protobuf contents for optional fields, tracing, target offset handling, block-group checksum metadata, and null optional values.
