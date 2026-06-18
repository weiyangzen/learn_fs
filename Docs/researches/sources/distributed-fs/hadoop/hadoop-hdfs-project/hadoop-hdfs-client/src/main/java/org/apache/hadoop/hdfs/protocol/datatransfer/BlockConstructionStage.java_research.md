# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/BlockConstructionStage.java

## Purpose
`BlockConstructionStage` enumerates the stages of HDFS block write, append, recovery, close, and transfer operations in the data transfer protocol.

## Important APIs, Types, and Functions
The enum values are ordered in regular/recovery pairs for append, streaming, and close. `PIPELINE_SETUP_CREATE`, `TRANSFER_RBW`, and `TRANSFER_FINALIZED` do not have recovery pairs. `getRecoveryStage` maps a regular stage to its recovery stage using `ordinal() | RECOVERY_BIT` and rejects `PIPELINE_SETUP_CREATE`.

## Control Flow
Callers use the enum to describe a `writeBlock` or transfer stage. Recovery mapping is purely ordinal-based.

## State and Persistence Behavior
Enum names are serialized through protobuf conversion in `DataTransferProtoUtil` by matching names. The ordinal order is also behaviorally significant for `getRecoveryStage`, even though protobuf uses names.

## Dependencies and Integration Points
It integrates with `DataTransferProtocol.writeBlock`, `Sender.writeBlock`, `DataTransferProtoUtil.toProto/fromProto`, DataNode block receiver/write pipeline code, and pipeline recovery logic.

## Risks and Edge Cases
Reordering enum values breaks `getRecoveryStage`. Adding new regular/recovery stages requires preserving the paired ordering rule. Calling `getRecoveryStage` on `PIPELINE_SETUP_CREATE` throws; calling it on already-recovery or transfer values can produce unintended enum values because only create is explicitly guarded.

## Test Signals
Pipeline recovery tests and write pipeline integration cover this indirectly. Unit tests should pin `getRecoveryStage` for each expected regular stage and reject unsupported stages.
