<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestIOUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestIOUtils.java

## Purpose
Unit tests for `IOUtils` stream copy/close policy, file-channel writes, compressed read error wrapping, skip semantics, directory listing, quiet close behavior, and exception wrapping.

## Important APIs, Types, and Functions
Uses `IOUtils.copyBytes` overloads, `writeFully`, `wrappedReadForCompressedData`, `skipFully`, `listDirectory`, `closeStreams`, and `wrapException`. Mockito mocks stream close/read behavior; real `RandomAccessFile` and `FileChannel` validate writes; `NoEntry3Filter` implements `FilenameFilter`.

## Control Flow and State
Copy tests verify close behavior for `close=true/false`, including output/input close exceptions and runtime exceptions. `testWriteFully()` writes a 10k byte array at current position and at an explicit halfway offset. `testWrappedReadForCompressedData()` converts an `InternalError` into an `IOException`. `testSkipFully()` checks exact premature EOF messages. Directory and close-stream tests create temporary filesystem state and clean it. `testWrapException()` checks reflection-based exception wrapping and fallback `PathIOException`.

## Dependencies and Integration Points
Integrates Java IO/NIO, Apache Commons `FileUtils`, Hadoop `PathIOException`, `GenericTestUtils`, and `LambdaTestUtils`. These utilities are used broadly across Hadoop filesystem and compression code.

## Risks and Test Signals
Risks include resource leaks, suppressed close exceptions, partial channel writes, exact EOF accounting, and platform filesystem cleanup. Signals are Mockito close verification, exact messages, on-disk byte comparisons, filtered directory membership, and exception class/path checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestIOUtils.java -->
