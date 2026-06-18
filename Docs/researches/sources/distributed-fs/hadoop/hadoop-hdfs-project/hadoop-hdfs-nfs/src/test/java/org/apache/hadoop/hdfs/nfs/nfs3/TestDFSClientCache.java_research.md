# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestDFSClientCache.java

## Purpose
`TestDFSClientCache` verifies caching and impersonation behavior in `DFSClientCache`, which is the user/namenode client source used by `RpcProgramNfs3`.

## Important APIs, Types, And Functions
Tests cover `getDfsClient`, cache eviction, `getUserGroupInformation`, and construction with multiple export points on the same namenode. Helper `isDfsClientClose` probes closed clients via `exists`.

## Control Flow
`testEviction` creates a cache of size one, fetches a client for `test1`, verifies reuse, fetches `test2`, then checks the first client was closed and the cache stayed bounded. Two UGI tests verify proxy UGI creation under Kerberos and simple login users. `testMultipleExportPointsSameNamenode` ensures duplicate export paths resolving to the same namenode do not throw false collision errors.

## State And Persistence
It mutates global `UserGroupInformation` state and resets it after each test. It creates DFSClient objects targeting `hdfs://localhost` but does not start a cluster in this file.

## Dependencies And Integration Points
It protects the client-cache layer used by all NFS RPC handlers. It depends on HDFS client close behavior, NFS export-point config, and Hadoop security UGI.

## Risks
The closed-client probe depends on exception text `Filesystem closed`. Tests do not exercise input-stream cache behavior or live NameNode interactions.

## Test Signals
Passing confirms bounded DFSClient caching, proxy user construction, Kerberos auth-method transition to PROXY, and same-namenode multi-export tolerance.
