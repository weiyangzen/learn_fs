# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestClientAccessPrivilege.java

## Purpose
`TestClientAccessPrivilege` verifies that export-table read-only privileges prevent mutating NFS operations, specifically REMOVE.

## Important APIs, Types, And Functions
The fixture uses `MiniDFSCluster`, `DistributedFileSystem`, `NameNode`, `Nfs3`, `RpcProgramNfs3.remove`, mocked `SecurityHandler`, and XDR request construction. The test method is `testClientAccessPrivilegeForRemove`.

## Control Flow
Setup configures proxy-user rules, starts MiniDFSCluster, chooses ephemeral NFS ports, and mocks the security user. Each test recreates `/tmp/f1`. The test sets exports to `* ro`, starts NFS, builds a REMOVE request for `f1` under the `/tmp` file handle, calls `nfsd.remove` directly, and asserts `NFS3ERR_ACCES`.

## State And Persistence
It creates and deletes `/tmp` content inside MiniDFSCluster. NFS service state is in-process and ephemeral.

## Dependencies And Integration Points
It directly targets `RpcProgramNfs3.checkAccessPrivilege` via the REMOVE path and depends on `NfsExports` parsing the allowed-hosts configuration.

## Risks
Only REMOVE is checked, so other write operations rely on parallel code patterns rather than this test. The NFS server is not explicitly stopped, and cluster shutdown occurs only after all tests.

## Test Signals
Passing confirms read-only export policy blocks a direct REMOVE handler call even when the mocked HDFS user has filesystem access.
