<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_operation_executor.cc -->
# sources/distributed-fs/lizardfs/src/common/read_operation_executor.cc

## Purpose
Implements one chunkserver read operation state machine for a single chunk part and read-plan entry. The source was read completely for this report.

## Important APIs, Types, And Functions
`sendReadRequest`, `continueReading`, `readAll`, `processHeaderReceived`, `processReadDataMessageReceived`, `processReadStatusMessageReceived`, `processDataBlockReceived`, and `setState` are the key functions.

## Control Flow
It serializes the correct read packet based on chunkserver version, sends it, then receives packet headers, READ_DATA prefixes, fixed-size data blocks, and READ_STATUS messages. It validates chunk id, offsets, sizes, status, and optional CRC before marking finished.

## State And Persistence Behavior
Runtime state includes message buffer, packet header, target data buffer pointer, chunk metadata, fd, state enum, current destination/bytes-left, completed block count, and current block CRC.

## Dependencies And Integration Points
Depends on sockets, protocol cltocs/cstocl serializers, `lizardfs_version`, CRC, exceptions, and `NetworkAddress`. Used by `ReadPlanExecutor` for parallel reads.

## Risks And Edge Cases
Assumes READ_DATA blocks are exactly `MFSBLOCKSIZE`; partial final read semantics must be handled by plan/request size/status protocol. Network errors mark chunkservers defective upstream.

## Test Signals
Needs protocol-fake tests for legacy/XOR/EC serialization, malformed headers, wrong ids/offsets/sizes, CRC mismatch, status errors, EAGAIN, timeout, and connection reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/read_operation_executor.cc -->
