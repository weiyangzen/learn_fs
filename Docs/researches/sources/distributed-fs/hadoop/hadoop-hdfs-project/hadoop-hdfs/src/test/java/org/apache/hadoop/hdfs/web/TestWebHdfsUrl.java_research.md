# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestWebHdfsUrl.java

## Purpose
`TestWebHdfsUrl` verifies WebHDFS URL construction, query-parameter selection, and path encoding behavior for simple users, proxy users, secure delegation-token clients, batched listings, access checks, and special-character filenames.

## Important APIs, types, and functions
- `resetUGI()` restores UGI to a fresh simple configuration before each test.
- `getWebHdfsFileSystem(UserGroupInformation, Configuration)` installs a synthetic WebHDFS delegation token in secure mode and returns a `WebHdfsFileSystem` for `webhdfs://127.0.0.1:0`.
- `checkQueryParams(String[], URL)` sorts expected and actual query fragments to assert exact parameter sets independent of order.
- Tests call `WebHdfsFileSystem.toUrl` with `GetOpParam`, `PutOpParam`, `TokenArgumentParam`, `DelegationParam`, `DoAsParam`, `UserParam`, `FsActionParam`, and `StartAfterParam`.

## Control flow
The first group builds URLs without a real cluster and checks that encoded path components and auth parameters round-trip correctly. Simple mode should include `user.name`; simple proxy mode should include real user plus `doas`; secure mode should avoid `user.name`, use delegation tokens for ordinary operations, and include `doas` for proxy token-management operations. Later tests start a `MiniDFSCluster` through `WebHdfsTestUtil.createConf()`, create files with punctuation-heavy names, then verify `getFileStatus` and `listFiles` preserve path names. The final semicolon/plus/percent regression creates files via WebHDFS and validates their names through the direct DFS client.

## State and persistence behavior
Most tests mutate only process UGI state and generated URL objects. The synthetic secure token path creates a `DelegationTokenSecretManager`, starts its threads, and adds a token to the supplied UGI. Cluster-backed tests persist files under MiniDFSCluster namespaces and shut the cluster down in `finally` or try-with-resources.

## Dependencies and integration points
This class integrates WebHDFS resource parameter classes, `SecurityUtil`, `UserGroupInformation`, `DelegationTokenSecretManager`, `FSNamesystem` mocks, `NetUtils`, `DFSTestUtil`, direct `DistributedFileSystem`, and the `WebHdfsTestUtil` helper. It tests a client/server contract between URL encoding in WebHDFS and path decoding in NameNode/DataNode WebHDFS handlers.

## Risks and edge cases
The query tests use an endpoint with port `0` and synthetic tokens, so they validate client URL construction rather than live server acceptance. Path tests are sensitive to encoding rules for `%`, `+`, semicolon, ampersand, comma, braces, quotes, and legacy percent treatment. The helper starts a token secret-manager thread without explicit shutdown in this file, which is acceptable for short tests but is a lifecycle risk.

## Test signals
Useful signals include exact URL query contents for auth/proxy/token cases, preservation of already percent-encoded path text, `CHECKACCESS` action encoding, `LISTSTATUS_BATCH` `startafter` encoding, and MiniDFSCluster proof that special-character paths can be created, listed, and read back without name corruption.
