# `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/DebugAdmin.java`

## Purpose

`DebugAdmin` implements `hdfs debug`, a collection of advanced diagnostic and recovery commands: metadata checksum verification, metadata checksum generation, lease recovery, and erasure-coded block-group verification. These commands are explicitly unstable and risky; several operate directly on block metadata files or DataNode block readers.

## Important APIs, Types, and Functions

- `DebugCommand` is the small command interface with name, usage, help, and `run`.
- `VerifyMetaCommand` reads a DataNode block metadata file header, reports checksum type, and optionally verifies checksum chunks against a local block file.
- `ComputeMetaCommand` creates a metadata file for a local block file using checksum options from configuration and `FsDatasetUtil.computeChecksum`.
- `RecoverLeaseCommand` opens a filesystem for the path URI, requires `DistributedFileSystem`, and retries `recoverLease` up to `-retries`.
- `VerifyECCommand` validates a closed erasure-coded file by reading each internal block from DataNodes, recomputing parity with a raw erasure encoder, and comparing computed parity buffers to stored parity blocks.
- `popCommand`, `run`, and `printUsage` implement command dispatch and generic help.

## Control Flow

`main` runs the `DebugAdmin` tool. `run` converts argv to a mutable list, removes the first matching command, and invokes it. Unknown/no command prints usage and returns success-like `0`, while command I/O/runtime failures print stack summaries and return `1`.

`verifyMeta` reads the metadata header first. If no `-block` is supplied, it stops after printing checksum type. With a block file, it reads data chunks and matching checksum bytes in buffers, then calls `DataChecksum.verifyChunkedSums` until EOF.

`computeMeta` validates the input block exists and output metadata does not exist, writes a metadata header, closes it, then asks `FsDatasetUtil.computeChecksum` to fill checksums.

`recoverLease` loops until recovery succeeds or retries are exhausted, sleeping five seconds between attempts with `Uninterruptibles.sleepUninterruptibly`.

`verifyEC` loads file status and located blocks, rejects missing/non-file/open/non-EC files, creates a raw encoder and thread-pool-backed `CompletionService`, then for each selected block group parses internal blocks, creates block readers, reads all data/parity buffers in parallel, zero-fills short reads, encodes data into parity outputs, and compares parity buffers. Readers are closed after each group.

## State and Persistence Behavior

`VerifyMetaCommand` is read-only. `ComputeMetaCommand` creates a local metadata file and is dangerous if used to replace real DataNode metadata. `RecoverLeaseCommand` mutates NameNode lease state for the target HDFS file. `VerifyECCommand` is intended read-only against HDFS blocks but opens direct DataNode peers and consumes cluster/network resources. The `VerifyECCommand` object holds per-run DFS client, EC layout, encoder, read service, and block reader arrays.

## Dependencies and Integration Points

The file integrates with DataNode metadata classes (`BlockMetadataHeader`, `FsDatasetUtil`), HDFS client internals (`DFSClient`, `BlockReaderRemote`, `LocatedStripedBlock`, `StripedBlockUtil`), erasure coding (`CodecUtil`, `RawErasureEncoder`, `ErasureCoderOptions`), direct DataNode networking (`Peer`, block tokens), `DistributedFileSystem`, and Hadoop checksum utilities.

## Risks and Edge Cases

- `computeMeta` can make corrupt data appear valid if operators overwrite real metadata with generated checksums.
- `VerifyECCommand` assumes at least one location for each internal block and uses the first location only; unavailable first replicas can fail verification even if other replicas exist.
- The read executor created for EC verification is not explicitly shut down in this class, which can matter for repeated in-process invocations.
- Parity comparison uses `ByteBuffer.equals`, so positions/limits must remain exactly aligned.
- Assertions check checksum consistency but are disabled unless Java assertions are enabled.
- Direct block reading and one-minute future waits can hang or fail under slow DataNodes.

## Test Signals

Tests should cover metadata header parse failures, checksum mismatch offsets, output-file-exists protection, lease retry behavior and non-HDFS rejection, EC verification on healthy and corrupted stripes, missing internal block handling, first-location failure behavior, `-skipFailureBlocks`, `-blockId` filtering, and cleanup of block readers.
