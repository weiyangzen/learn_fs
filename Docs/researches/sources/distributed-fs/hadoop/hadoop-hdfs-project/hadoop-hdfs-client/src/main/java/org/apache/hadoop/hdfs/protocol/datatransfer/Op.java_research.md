# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/datatransfer/Op.java

## Purpose
`Op` defines one-byte operation codes for the HDFS data transfer protocol.

## Important APIs, Types, and Functions
Codes range from `WRITE_BLOCK` 80 through `BLOCK_GROUP_CHECKSUM` 90, with `CUSTOM` 127. `read(DataInput)` reads a byte and maps it to an enum with a private `valueOf(byte)`. `write(DataOutput)` writes the code.

## Control Flow
The mapping subtracts `FIRST_CODE` and indexes into `values()`, returning null for out-of-range codes. This assumes the enum values from 80 through 90 are contiguous and ordered exactly like their codes.

## State and Persistence Behavior
The byte codes are wire protocol state and must remain stable. There is no runtime mutable state.

## Dependencies and Integration Points
It integrates with `Sender.op`, DataNode operation dispatch, and all data transfer protocol readers/writers.

## Risks and Edge Cases
Adding an enum value before `CUSTOM` or creating non-contiguous codes can break `valueOf(byte)` because it indexes by ordinal. `CUSTOM` at 127 is not contiguous with 80-90, so reading byte 127 currently maps outside the contiguous range and returns null rather than `CUSTOM`.

## Test Signals
Data transfer protocol tests should pin every opcode byte and read/write round trip. A focused test should document the `CUSTOM` read behavior if intentional.
