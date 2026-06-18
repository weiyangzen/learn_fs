# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/StripedFileTestUtil.java

## Purpose
`StripedFileTestUtil` is a shared utility class for HDFS erasure-coded striped-file tests. It generates deterministic data, validates read/seek behavior, inspects striped block groups, verifies parity bytes, waits for reporting/reconstruction, and supplies EC policies for parameterized tests.

## Important APIs, Types, and Functions
- `generateBytes(int)` and `getByte(long)` define deterministic file content using a modulo-29 pattern.
- `verifyLength`, `verifyPread`, `verifyStatefulRead` for byte arrays and `ByteBuffer`, `verifySeek`, and `assertSeekAndRead` validate file contents through multiple read APIs and boundary seeks.
- `killDatanode` and `getDatanodes` work with `DFSStripedOutputStream` and `StripedDataStreamer` to stop the DN currently used by a streamer.
- `getRealDataBlockNum` and `getRealTotalBlockNum` calculate internal block counts for partial stripes.
- `waitBlockGroupsReported` polls located blocks until expected internal block locations are reported.
- `randomArray` returns unique random integers in a range for block selection.
- `verifyLocatedStripedBlocks` asserts block groups are `LocatedStripedBlock`s with distinct locations and complete block-index sets.
- `checkData` parses striped block groups, reads internal blocks with `BlockReader`, verifies data-block bytes, fills killed data for parity verification, and calls `verifyParityBlocks`.
- `verifyParityBlocks` recomputes parity using Hadoop raw erasure encoders and compares expected parity blocks.
- `waitForReconstructionFinished` and `waitForAllReconstructionFinished` poll until reconstructed located-block counts reach expectations.
- `getLocatedBlocks`, `getDefaultECPolicy`, `getRandomNonDefaultECPolicy`, and `getECPolicies` expose common EC test inputs.

## Control Flow
Read verification writes expected data once and exercises positional reads from offsets around cell, stripe, block-group, and EOF boundaries. Stateful reads stream the full file into arrays/buffers and compare to expected bytes. Seek verification checks valid positions and, except for WebHDFS streams, asserts negative and past-EOF seeks fail.

Block-group reporting polls DFSClient located blocks up to 40 times and compares each block group's reported locations to the expected internal block count minus known dead DNs. `checkData` parses each striped block group into internal blocks, calculates each internal block's expected size, reads live blocks directly, verifies data bytes by translating internal offsets to file offsets, and recomputes parity for available parity blocks.

Reconstruction waits poll for enough located storage entries on the last block group or across all groups. EC policy helpers read system policies and package them for parameterized tests.

## State and Persistence Behavior
The class is stateless except for logging. It reads from and writes to HDFS through callers, stops DataNodes through MiniDFSCluster, and may directly read internal blocks through block readers. Randomness appears in `randomArray` and `getRandomNonDefaultECPolicy`, which affects reproducibility.

## Dependencies and Integration Points
It integrates with `DistributedFileSystem`, `FSDataInputStream`, `DFSStripedOutputStream`, `StripedDataStreamer`, `BlockReaderTestUtil`, `LocatedStripedBlock`, `StripedBlockUtil`, `SystemErasureCodingPolicies`, `CodecUtil`, raw erasure encoders, WebHDFS input streams, MiniDFSCluster, and JUnit assertions. Many EC tests depend on these helpers for common correctness checks.

## Risks and Edge Cases
- `randomArray` returns `null` for invalid ranges, and callers must assert/check that.
- `verifyPread` clamps offsets, so very small files still get repeated edge reads at valid offsets.
- `getDatanodes` spins until streamer nodes appear and can return `null` only on interruption.
- `checkData` assumes `killedList` is non-null and uses direct block reads, so it is sensitive to block-location availability and internal block sizing calculations.
- `verifyParityBlocks` normalizes shorter data blocks by padding to the first data block length; mistakes here could hide or expose parity-size bugs depending on last-block-group shape.
- `getRandomNonDefaultECPolicy` assumes at least one non-default policy exists.

## Test Signals
The utility's assertions are high-signal correctness checks for EC read paths: exact bytes, length, seek exceptions, unique placement, complete internal block indexes, generation-stamp monotonicity, direct internal block sizes, parity recomputation, and reconstruction location counts. Timeouts indicate reporting or reconstruction regressions.
