# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/PipelineAck.java

## Purpose
`PipelineAck` represents acknowledgement messages flowing back through an HDFS write pipeline. It carries a sequence number, per-DataNode statuses, optional per-reply flags for ECN and slow-node signaling, and downstream ack latency.

## Important APIs, Types, and Functions
`UNKOWN_SEQNO` (`-2`, misspelled in the constant name) identifies out-of-band acks. `SLOW` and `ECN` enums each occupy two bits in a packed header. `StatusFormat` uses `LongBitFormat` to pack status (4 bits), a reserved bit, ECN bits, and slow bits.

Constructors build a `PipelineAckProto` from a seqno, packed reply headers, and optional downstream ack time. `getHeaderFlag` returns stored flags when available or synthesizes old-format flags from the reply status with disabled ECN/SLOW. `isSuccess` checks all statuses. `getOOBStatus` returns OOB statuses only when seqno is `UNKOWN_SEQNO`. `readFields` parses a vint-prefixed protobuf, and `write` writes a delimited protobuf.

Static helpers combine and extract status/ECN/SLOW fields and expose restart OOB status checks.

## Control Flow
DataNodes construct acks with per-hop reply headers; clients/DataStreamer parse them and decide success, retry, congestion, or slow-node handling. Old protobufs without `flag` fields remain readable because `getHeaderFlag` synthesizes default flags.

## State and Persistence Behavior
The mutable `proto` field is populated by constructors or `readFields`. The protobuf wire format and packed bit allocation are compatibility-sensitive. Downstream ack time is transient performance telemetry in the ack.

## Dependencies and Integration Points
It depends on DataTransfer protobufs, `Status`, `LongBitFormat`, `PBHelperClient.vintPrefixed`, and Hadoop test visibility annotations. It integrates with `DataStreamer`, DataNode `BlockReceiver`, pipeline recovery, ECN/slow-node detection, and data transfer tests.

## Risks and Edge Cases
`SLOW.valueOf(int)` and `ECN.valueOf(int)` index arrays without range checks; invalid packed bits can throw. OOB detection depends on protobuf enum numeric ordering. Backward compatibility with old acks depends on `getHeaderFlag` fallback. The typo in `UNKOWN_SEQNO` is part of the API and should not be casually renamed.

## Test Signals
`TestDataTransferProtocol` covers old/new ack compatibility and ECN/SLOW flags. `TestClientProtocolForPipelineRecovery` and `TestDataNodeECN` cover pipeline behavior. Focused tests should pin bit packing, old-proto fallback, OOB status range, and invalid packed header behavior.
