# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/shortcircuit/TestShortCircuitLocalRead.java

## Purpose
`TestShortCircuitLocalRead` verifies local short-circuit HDFS block reads, including checksum and no-checksum modes, legacy block reader permissions/fallback, positional reads, direct `ByteBuffer` reads, skip/seek behavior, corrupt local block-file handling, remote block reader fallback behavior, and the deprecated `getBlockLocalPathInfo` permission gate. It also contains a standalone benchmark-oriented `main` method for comparing short-circuit and regular reads.

## Important APIs, Types, And Functions
The fixture uses `TemporarySocketDirectory` and `DomainSocket.disableBindPathValidation()` in `@BeforeAll`, with a per-test `assumeTrue` that native domain sockets loaded. `createFile` creates HDFS files using the configured block size. `checkFileContent` validates stream reads using `FSDataInputStream.readFully`, `IOUtils.skipFully`, small reads, chunk-boundary reads, and full reads. `checkFileContentDirect` repeats validation with `HdfsDataInputStream.read(ByteBuffer)` and a direct buffer. `doTestShortCircuitReadImpl` configures `HdfsClientConfigKeys.Read.ShortCircuit.KEY`, checksum skipping, random `DFS_CLIENT_CONTEXT`, domain socket path, optional legacy local-path user, and a one-DataNode MiniDFSCluster.

Other important APIs are `DFSUtilClient.createClientDatanodeProtocolProxy`, `ClientDatanodeProtocol.getBlockLocalPathInfo`, `DFSTestUtil.getFirstBlock`, `MiniDFSCluster.getBlockFile`, `RandomAccessFile.setLength`, `ClientContext.getDisableLegacyBlockReaderLocal`, `UserGroupInformation.doAs`, and `SubjectInheritingThread` for benchmark workers.

## Control Flow
The core test path creates deterministic random file content, writes it to a one-replica file, opens the cluster URI as a selected user, then checks both byte-array and direct-buffer read APIs from offset zero or a supplied offset. Small/long/read-offset tests vary file length and checksum skipping. Legacy tests supply `DFS_BLOCK_LOCAL_PATH_ACCESS_USER_KEY`; the fallback test reads as an unauthorized user and verifies legacy local reads become disabled after fallback.

The deprecated RPC test creates a block, obtains a block token and DataNode info, calls `getBlockLocalPathInfo` without configuring an allowed user, and expects an explanatory IOException. The skip test forces a short-circuit read before seeking across two blocks. The truncated block test writes two files, records the second file's content, truncates the first file's local block file to zero after cluster shutdown, restarts without formatting, verifies the corrupt file read fails, and then confirms the unrelated file still reads correctly. The remote block reader test enables short-circuit but omits a domain socket path, then confirms ordinary content reads still work and direct `ByteBuffer` read does not hit an unsupported-method failure.

## State And Persistence Behavior
Persistent state includes HDFS file contents, local DataNode block files, block tokens, client context flags, and optional legacy short-circuit disablement. The truncated-block test deliberately mutates the local block file on disk between cluster lifecycles to exercise corruption detection across restart. User identity state is simulated with `UserGroupInformation.createRemoteUser` and `doAs`; benchmark threads inherit subject state. Domain socket paths live in a temporary directory closed after all tests.

## Dependencies And Integration Points
The suite integrates DFSClient read paths, `BlockReaderLocal`, `HdfsDataInputStream`, legacy local block reader access control, DataNode local-path RPC, block-token security, domain sockets, and MiniDFSCluster local storage. It depends on `AppendTestUtil` for deterministic data, `TestBlockReaderLocal.assertArrayRegionsEqual` for byte comparison in one corruption path, and HDFS client configuration keys for short-circuit behavior.

## Risks And Edge Cases
Important edge cases are unauthorized legacy local reads falling back without data corruption, direct-buffer reads across chunk boundaries, offsets into small and multi-block files, skip with checksum verification enabled, distinguishing corrupt local data from communication failure, and ensuring one corrupt block file does not poison reads of another file. The benchmark `main` is not a JUnit test and assumes an external HDFS configuration, so it is more operational utility than CI signal.

## Test Signals
Signals are exact byte-for-byte comparisons against deterministic data, expected toggling of `ClientContext.getDisableLegacyBlockReaderLocal`, IOException text for unauthorized local-path RPC, failed reads from a zero-length block file, successful reads from the unaffected file after corruption, and command-return assertions in the remote-reader path.
