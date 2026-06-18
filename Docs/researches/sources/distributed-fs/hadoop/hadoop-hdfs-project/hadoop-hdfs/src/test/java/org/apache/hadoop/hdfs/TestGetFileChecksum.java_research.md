# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestGetFileChecksum.java

## Purpose
Validates HDFS file checksum semantics for appended files and rejects checksums for files with blocks under construction.

## APIs and Control Flow
`setUp` builds a three-DN cluster with 1024-byte blocks. `testGetFileChecksum(Path,int)` creates a file, records the full checksum after each of 16 append rounds, then calls `getFileChecksum(path, prefixLength)` and verifies each prefix checksum matches the earlier whole-file checksum at that length. `testGetFileChecksumForBlocksUnderConstruction` writes to an unclosed stream and expects `getFileChecksum` to fail with an under-construction message. `testGetFileChecksum` runs aligned and unaligned append lengths.

## State, Dependencies, Integration
State is block checksum metadata across appends and open-file construction state. Dependencies include `DFSTestUtil`, `FileChecksum`, `FSDataOutputStream`, and `DistributedFileSystem`. It integrates append, checksum prefix API, and open-block validation.

## Risks and Test Signals
Signals are checksum equality across append history and explicit IOException message content. Risks include brittle message text and possible timing around open stream visibility, though the under-construction stream is deliberately left open.
