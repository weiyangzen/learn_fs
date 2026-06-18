# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestBlockTokenWithDFS.java

## Purpose
`TestBlockTokenWithDFS` is an integration test for HDFS block access tokens across read, write, append, direct datanode access, namenode restarts, datanode restarts, and balancer integration. It verifies that expired or malformed block tokens fail at the datanode, while DFS clients can transparently refetch valid tokens when the namenode is available.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `DFSClient`, `NamenodeProtocols`, `BlockManager`, `BlockTokenSecretManager`, `LocatedBlock`, `ExtendedBlock`, and `BlockReaderFactory`. Helpers include `generateBytes`, `createFile`, `checkFile1`, `checkFile2`, `writeFile`, `tryRead`, `getConf`, `doTestRead`, and `isBlockTokenExpired`. `tryRead` builds a low-level `BlockReader` with a custom `RemotePeerFactory`, making it a direct test of datanode token validation rather than only the high-level `FileSystem` API.

## Control Flow
`testAppend` and `testWrite` set a one-second token lifetime, write part of a block, wait for the stream token to expire, stop a datanode to force pipeline recovery, then finish the operation and validate bytes. `testRead` builds a two-datanode cluster and delegates to `doTestRead`. `doTestRead` creates a file, opens several streams to cache tokens, exercises direct block reads, waits for token expiry, checks failure for expired/wrong-block/wrong-access tokens, lengthens future token lifetime, verifies transparent token refresh, then tests cached-token behavior across datanode and namenode restarts. `testEnd2End` runs the balancer integration with block tokens enabled.

## State and Persistence Behavior
State under test lives in block tokens cached in `FSDataInputStream` instances, token secret-manager lifetime settings, restarted datanode ports, restarted namenode secret state, and block-location metadata returned by the namenode. The test intentionally takes the namenode down to prove whether cached tokens alone are sufficient.

## Dependencies and Integration Points
This file integrates HDFS client streams, `BlockReaderFactory`, datanode transfer sockets, namenode RPC block locations, token secret management, cluster restart paths, and `TestBalancer`. It relies on `DFSTestUtil`, `SecurityTestUtil`, `GenericTestUtils`, and `ServerSocketUtil`.

## Risks and Edge Cases
The test is sensitive to timing around token expiry and cluster restarts. It covers important risks: stale cached tokens after DN/NN restarts, wrong block IDs, wrong access modes, and pipeline recovery using expired tokens. Port choices are pinned for namenode restart stability.

## Test Signals
Assertions verify exact byte equality, token expiry/non-expiry, `InvalidBlockTokenException` on invalid direct reads, successful transparent rereads after refetch, failed reads when the namenode is unavailable and cached tokens no longer work, and successful balancer integration with block tokens.
