# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/test_libhdfs_zerocopy.c

## Purpose
`test_libhdfs_zerocopy.c` validates libhdfs zero-copy read APIs against a MiniDFSCluster configured for short-circuit reads. It checks buffer contents, read statistics, checksum/pool option behavior, zero-length reads, EOF handling, and release semantics.

## Important APIs and helpers
`getZeroCopyBlockData` creates deterministic block contents. `getZeroCopyBlockLen` models five full blocks and one shorter final block. `createZeroCopyTestFile` writes the deterministic file. `nmdConfigureHdfsBuilder` configures the builder with NameNode port and optional short-circuit domain socket path. `doTestZeroCopyReads` exercises `hadoopRzOptions`, `hadoopReadZero`, `hadoopRzBufferGet`, `hadoopRzBufferLength`, and `hadoopRzBufferFree`.

## Control flow
The test starts a formatted MiniDFSCluster with `configureShortCircuit=1`, configures a forced-new HDFS builder with block size and `dfs.client.read.shortcircuit.skip.checksum=true`, writes a deterministic file, then reads it through zero-copy. It first reads half-block chunks and a small read with `skipChecksum` enabled, validates file statistics, disables skip-checksum with no `ByteBufferPool` and expects `EPROTONOSUPPORT`, then sets `ElasticByteBufferPool` and verifies reads succeed. It finally checks zero-length read returns a non-NULL empty buffer and EOF returns a buffer with NULL data.

## State and persistence
The test creates a random `/zeroCopyTestFile.<pid>.<rand>` path in the MiniDFSCluster. `hadoopRzOptions` caches options and optional byte buffer pool state. Each returned `hadoopRzBuffer` must be released to the stream with `hadoopRzBufferFree`.

## Dependencies
It depends on `native_mini_dfs`, libhdfs zero-copy APIs, `expectFileStats` from `expect.c`, short-circuit local reads, domain socket configuration, and Java `ElasticByteBufferPool`.

## Risks
Zero-copy behavior is sensitive to platform support for domain sockets, mmap/direct buffers, short-circuit configuration, and checksum settings. The test exits directly on allocation failure in `getZeroCopyBlockData`, so failures there bypass cluster cleanup. The expected statistics depend on Hadoop `ReadStatistics` semantics and can break if counters change.

## Test signals
Primary signals are exact byte comparisons for split block boundaries, expected `hdfsTell`, read statistics totals including zero-copy bytes, `EPROTONOSUPPORT` when no pool/checksum combination is unsupported, success with a ByteBufferPool, correct zero-length and EOF buffer shapes, and clean cluster shutdown.
