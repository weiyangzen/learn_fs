# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDebugAdmin.java

## Purpose
`TestDebugAdmin` exercises HDFS `DebugAdmin` subcommands for lease recovery, block metadata verification, metadata recomputation, and erasure-coded file verification.

## Important APIs, Types, And Functions
The file uses `DebugAdmin`, `MiniDFSCluster`, `DistributedFileSystem`, `DFSTestUtil`, `FsDatasetSpi`, `ExtendedBlock`, `LocatedStripedBlock`, `StripedBlockUtil`, `SystemErasureCodingPolicies`, `FsDatasetTestUtil.getBlockFile/getMetaFile`, and Apache Commons `FileUtils`. `runCmd(String[])` redirects both stdout and stderr, invokes `admin.run`, and normalizes line separators into a single assertion string.

## Control Flow
Each test starts an appropriate MiniDFSCluster, creates files, locates block and metadata files from DataNode datasets, runs debug commands, and asserts exact return/status output. `testVerifyECCommand` creates an EC directory, verifies many file sizes, corrupts local striped block bytes, recomputes checksums with `computeMeta`, and verifies that `verifyEC` reports mismatched EC compute results. It also tests `-blockId` and `-skipFailureBlocks`.

## State, Persistence, And Dependencies
State includes local block files, metadata checksum files, HDFS file lease state, EC policy settings, and captured process streams. The test mutates DataNode local storage directly to create corruption and writes output metadata under a test root. Cluster teardown is the main cleanup path.

## Integration Points
This bridges CLI argument handling with DataNode on-disk block layout, metadata checksum readers/writers, lease recovery APIs, HDFS EC placement, and striped block parsing.

## Risks
The EC corruption test is highly coupled to block placement, local DataNode storage paths, block-group parsing, and exact DebugAdmin output text. Directly replacing block files and deleting meta files can leave cluster state inconsistent if assertions fail mid-test. Output normalization removes line separators, so regressions in formatting may be obscured if text still concatenates similarly.

## Test Signals
Signals include exact help/error strings and return codes, created metadata file existence and length, successful checksum verification, "All EC block group status: OK", and error output for intentionally corrupted EC data.
