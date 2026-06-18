# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestAppendDifferentChecksum.java

## Purpose
`TestAppendDifferentChecksum` verifies HDFS append behavior when a file is written with one checksum configuration and appended with another. It focuses on checksum algorithm changes, while chunk-size switching remains disabled.

## Important APIs, Types, and Functions
- `setupCluster()` creates a one-DataNode MiniDFSCluster with 4096-byte blocks and disables HDFS filesystem caching.
- `teardown()` shuts down the cluster after all tests.
- `testSwitchChunkSize()` is disabled because appending with a different bytes-per-checksum chunk size is not implemented.
- `testSwitchAlgorithms()` writes with CRC32 and appends with CRC32C, then verifies reads through both clients.
- `testAlgoSwitchRandomized()` repeatedly appends random-length segments using randomly selected CRC32 or CRC32C clients for roughly five seconds, then validates the entire file through both clients.
- `createFsWithChecksum(String type, int bytes)` clones the cluster config and sets checksum type and bytes-per-checksum.
- `appendWithTwoFs(Path, FileSystem, FileSystem)` writes one deterministic segment with the first FS and appends a second segment with the second FS.

## Control Flow
The cluster is shared for the class. Tests create separate `FileSystem` clients with different checksum settings. The simple algorithm-switch test writes two fixed 1500-byte segments and uses `AppendTestUtil.check` to verify expected deterministic contents. The randomized test creates an empty file, loops until the runtime budget expires, appends a random segment length below 500 bytes using a random checksum client, tracks total length, and verifies final content with both clients.

## State and Persistence Behavior
The tests persist files in MiniDFSCluster and rely on HDFS storing checksum metadata per block/chunk such that readers use on-disk checksums rather than their current client preference. The randomized test's file length and segment sequence are driven by a time-based seed printed to stdout.

## Dependencies and Integration Points
Dependencies include MiniDFSCluster, HDFS checksum config keys, `FileSystem`, `FSDataOutputStream`, `AppendTestUtil`, Hadoop `Time`, `IOUtils`, JUnit lifecycle/timeout/disabled annotations, and Java `Random`.

## Risks and Edge Cases
- The randomized test is time-based and seed-based, so coverage and failure reproduction depend on the printed seed.
- The timeout is twice the runtime budget, leaving limited room for slow CI.
- The disabled chunk-size test documents a known unsupported behavior, so algorithm-switch support must not be confused with bytes-per-checksum switching.
- Created checksum-specific FileSystem instances are not explicitly closed in each test, though filesystem caching is disabled.

## Test Signals
Passing algorithm-switch tests show appends with CRC32 and CRC32C can coexist and be read correctly by clients configured for either algorithm. The disabled test is a signal that checksum chunk-size switching remains intentionally unsupported.
