# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestReaddir.java

## Purpose
`TestReaddir` verifies NFS READDIR and READDIRPLUS responses for initial cookies, resume cookies, and deleted-cookie recovery.

## Important APIs, Types, And Functions
The suite uses `MiniDFSCluster`, `DistributedFileSystem`, `NameNode`, `Nfs3`, `RpcProgramNfs3.readdir`, `RpcProgramNfs3.readdirplus`, NFS `FileHandle`, XDR request construction, and mocked `SecurityHandler`.

## Control Flow
Setup configures proxy users, starts MiniDFSCluster and NFS, and mocks the current user. Before each test, `/tmp` is recreated with files `f1`, `f2`, and `f3`. `testReaddirBasic` sends cookie-zero READDIR, expects dot/dotdot plus three files, then uses `f2`'s file ID as a resume cookie and expects only `f3`; after deleting `f2`, the same cookie causes listing restart without dot/dotdot and returns two entries. `testReaddirPlus` repeats the same scenarios while expecting attributes and handles in entries.

## State And Persistence
It mutates MiniDFSCluster filesystem contents under `/tmp`. NFS and HDFS cluster state live for the class and are shut down after all tests.

## Dependencies And Integration Points
It directly covers `RpcProgramNfs3.listPaths`, cookie-to-inode-id path conversion, dot/dotdot special handling, and READDIRPLUS child attribute lookup through `WriteManager.getFileAttr`.

## Risks
The tests assume stable HDFS listing order and file-id cookie behavior. They do not assert cookie verifier mismatch handling, count truncation, non-directory errors, or export privilege failures.

## Test Signals
Passing confirms basic directory enumeration, resume-after-cookie semantics, and recovery when the cookie's start-after entry has been deleted.
