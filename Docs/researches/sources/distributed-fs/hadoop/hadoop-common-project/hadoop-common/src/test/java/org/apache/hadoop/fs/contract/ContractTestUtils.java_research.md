# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ContractTestUtils.java

## Purpose
`ContractTestUtils` is the shared test utility library for Hadoop filesystem contract suites. It creates deterministic datasets, writes and reads files, validates byte-for-byte results, asserts path state, handles cleanup safely, builds synthetic directory trees, verifies vectored read results, converts iterators, and records simple performance timings.

## Important APIs, Types, And Functions
Important file APIs include `writeAndRead()`, `writeDataset()`, `readDataset()`, `readDatasetSingleByteReads()`, `readNBytes()`, `verifyFileContents()`, `verifyRead()`, `compareByteArrays()`, `dataset()`, `writeTextFile()`, `createFile()`, `appendFile()`, `touch()`, `file()`, and `createAndVerifyFile()`. Path helpers include `cleanup()`, `rm()`, `rename()`, `rejectRootOperation()`, `deleteChildren()`, `listChildren()`, `assertDeleted()`, `assertRenameOutcome()`, `assertPathExists()`, `assertPathDoesNotExist()`, `assertIsFile()`, `assertIsDirectory()`, `assertMkdirs()`, and capability assertions for `StreamCapabilities` and `PathCapabilities`. Vectored helpers include `range()`, `totalReadSize()`, `validateVectoredReadResult()`, `returnBuffersToPoolPostRead()`, and `assertDatasetEquals()`. Nested `TreeScanResults` tracks files, directories, and other entries; `NanoTimer` records elapsed time and bandwidth.

## Control Flow
Most helpers perform an operation, then immediately verify observable filesystem state. Write helpers close streams in `finally`/try-with-resources and then assert length. Read helpers loop until requested bytes are obtained or throw `EOFException`. Cleanup shields callers from null filesystems and logs deletion failures. Tree creation recurses depth-first and records expected entries for later comparison. Vectored read validation waits for every range future and compares returned `ByteBuffer` contents to the original dataset at each offset.

## State And Persistence
The class itself is stateless except for constants. Files, directories, stream statistics, and temporary datasets are the persistent side effects. `TreeScanResults` stores path lists and counts; `NanoTimer` stores start/end timestamps.

## Dependencies And Integration Points
It depends on Hadoop `FileSystem`, `FileContext`, `FSDataInputStream`, `FSDataOutputStream`, `FileRange`, `RemoteIterator`, `IOStatistics`, `ByteBufferPool`, `FutureIO`, AssertJ, JUnit assertions, and SLF4J. Abstract contract suites call these methods for setup, validation, and diagnostics.

## Risks
Root operation guards are critical because many contract suites can target real filesystems. Several helpers assume strong consistency unless a caller explicitly uses eventual helpers. Vectored helpers must return buffers to pools after validation or tests may leak memory. `compareByteArrays()` logs only a small window around the first mismatch, so large corruption patterns may need extra diagnostics.

## Test Signals
Strong signals are exact byte comparisons, verified path existence/deletion, duplicate-free tree comparisons, expected IOStatistics keys/counters, successful vectored futures within the five-minute timeout, and cleanup logs without root-operation rejection surprises.
