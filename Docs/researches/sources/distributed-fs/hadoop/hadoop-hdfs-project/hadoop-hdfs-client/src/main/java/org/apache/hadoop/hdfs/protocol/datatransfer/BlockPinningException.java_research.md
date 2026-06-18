# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/BlockPinningException.java

## Purpose
`BlockPinningException` is a specific `IOException` used when a data transfer operation fails because of block pinning constraints.

## Important APIs, Types, and Functions
The class has a single string constructor and a serial version UID.

## Control Flow
It is thrown by `DataTransferProtoUtil.checkBlockOpStatus` when the response status is `ERROR_BLOCK_PINNED` and the caller opted into checking block-pinning errors.

## State and Persistence Behavior
Only the inherited exception message is stored. It participates in normal Java/RPC exception handling.

## Dependencies and Integration Points
It integrates with data transfer response handling, block movement/replacement paths, and balancing/pinning behavior where pinned blocks should not be moved.

## Risks and Edge Cases
If callers do not pass `checkBlockPinningErr=true`, the same status becomes a generic `IOException`, losing semantic detail. Tests should cover both branches.

## Test Signals
Data transfer and balancer tests involving pinned blocks should assert this exception type when requested.
