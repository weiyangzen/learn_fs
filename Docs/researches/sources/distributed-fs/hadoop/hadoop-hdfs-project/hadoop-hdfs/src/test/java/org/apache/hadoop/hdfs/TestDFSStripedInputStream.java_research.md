<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedInputStream.java

## Purpose
This slow integration suite validates `DFSStripedInputStream` read behavior for HDFS erasure-coded striped files. It covers block refresh, positional reads, stateful reads, DataNode failures, decoding, buffer-pool cleanup, block-reader range calculation, unbuffering, and retry behavior after injected read-strategy failures.

## Important APIs, Types, and Functions
- `getEcPolicy` returns the default EC policy and is intentionally overridable by subclasses.
- Setup derives `dataBlocks`, `parityBlocks`, `cellSize`, `blockSize`, and `blockGroupSize`, configures simulated datasets, starts `MiniDFSCluster`, disables DataNode heartbeats, enables the EC policy, and sets it on `/striped`.
- `DFSTestUtil.createStripedFile`, `cluster.injectBlocks`, `StripedBlockUtil.parseStripedBlockGroup`, and `SimulatedFSDataset.simulatedByte` build deterministic expected striped contents.
- `CodecUtil.createRawDecoder` and `RawErasureDecoder` compute expected reconstructed bytes when a DataNode is stopped.
- `DFSClientFaultInjector` observes block-reader creation ranges and injects retry failures.
- `emptyBufferPoolForCurrentPolicy`, `verifyPreadRanges`, and `verifySreadRanges` are local helpers for buffer-pool and range tests.

## Control Flow
`testRefreshBlock` parses located striped block groups and verifies that refreshing component blocks preserves identity, offsets, and locations. `testPread` injects component blocks for two block groups and reads from offsets around cells, stripes, block-group boundaries, and EOF, comparing byte-by-byte to manually generated expected data.

Failure read tests stop one DataNode and use a raw decoder to precompute reconstructed bytes. They verify both positional and stateful read paths across partial cells and full remainder reads. `testStatefulRead` runs byte-array and `ByteBuffer` stateful reads and restarts the cluster with an unaligned IO buffer for misaligned packet coverage.

Lifecycle and edge tests verify idempotent close, error propagation when `blockSeekTo` fails before a current block is set, no buffer allocation during close, reconstruction when the last incomplete cell participates in aligned-stripe decode, `unbuffer` releasing current stripe and parity buffers, exact block-reader ranges for pread/sread, and stateful retry when the first read strategy fails with more-than-parity simulated failures.

## State and Persistence Behavior
Each test gets a fresh cluster rooted at a JUnit `@TempDir`. It persists EC policy on directories, writes striped files, injects simulated block replicas into specific DataNodes, stops DataNodes, mutates IO buffer configuration in one branch, and resets the cluster as needed. Buffer-pool state is inspected and drained for the current EC policy. `DFSClientFaultInjector` is global and is restored in the retry test.

## Dependencies and Integration Points
The suite directly covers `DFSStripedInputStream`, `DFSInputStream`, `DFSClient`, NameNode block-location RPCs, EC raw decoders, simulated DataNode datasets, block-group parsing, `ElasticByteBufferPool`, `FSDataInputStream`, and the fault-injection hooks used by HDFS clients.

## Risks
Manual expected-byte generation duplicates striping layout assumptions and can drift with implementation changes. Some loops rely on positive reads and exact lengths; a zero read would hang without timeout. DataNode heartbeats are disabled, so tests rely on explicit block reports and synthetic state. Global `DFSClientFaultInjector` must be restored to avoid cross-test pollution.

## Test Signals
Signals include exact byte-array equality, component block metadata equality, decoded-data equality after DataNode failure, null buffer assertions after `unbuffer`, exact block-reader range lists, exception-message containment, and complete write/read equality for large retry coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDFSStripedInputStream.java -->
