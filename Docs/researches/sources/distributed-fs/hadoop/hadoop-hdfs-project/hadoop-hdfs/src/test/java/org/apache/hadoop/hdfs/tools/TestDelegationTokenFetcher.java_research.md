# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestDelegationTokenFetcher.java

## Purpose
`TestDelegationTokenFetcher` verifies token fetch, save, renew, cancel, print, null-token, and failure paths for `DelegationTokenFetcher` over WebHDFS and RPC.

## Important APIs, Types, And Functions
The test uses `DelegationTokenFetcher`, `WebHdfsFileSystem`, `DistributedFileSystem`, `MiniDFSCluster`, `Credentials`, `Token<DelegationTokenIdentifier>`, `FakeRenewer`, `LocalFileSystem`, Mockito stubbing, and `DFS_NAMENODE_DELEGATION_TOKEN_ALWAYS_USE_KEY`.

## Control Flow
Mock-based tests force `getDelegationToken` to throw, return a concrete token, or return null, then call `saveDelegationToken` and inspect the token storage file. The RPC test starts a zero-DataNode cluster with delegation tokens always enabled, fetches a token without a renewer, prints it in verbose and nonverbose modes, and confirms renewal fails with an `AccessControlException`.

## State, Persistence, And Dependencies
Token state is persisted to temporary local token files via `Credentials.writeTokenStorageFile` behavior. `FakeRenewer` captures last renewed/canceled tokens. The MiniDFSCluster path depends on HDFS security token configuration even in a test cluster.

## Integration Points
The file links WebHDFS token retrieval, HDFS RPC token retrieval, Hadoop credentials serialization, token renewer plugins, and user-visible token-print formatting.

## Risks
Mockito coverage validates fetcher logic without a real HTTP server for most WebHDFS paths. The expected nonverbose prefix includes the process user name and empty renewer, so it is sensitive to token display format changes. Raw `Token` use in the RPC test suppresses type specificity.

## Test Signals
Signals include thrown `IOException` on fetch failure, byte-for-byte token identifier/password equality after storage reload, `FakeRenewer` renew/cancel captures, absence of a file for null token, and a renewal denial message for tokens without renewers.
