# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestRpcProgramNfs3.java

## Purpose
JUnit 5 integration coverage for `RpcProgramNfs3`, exercising the Hadoop NFSv3 server implementation against a live `MiniDFSCluster`. It validates the basic NFS procedure surface, host/export authorization through mocked `SecurityHandler` identities, encrypted-zone read/write behavior, idempotency metadata, and deprecated configuration-key compatibility.

## Important APIs, Types, and Functions
The fixture owns static cluster state: `MiniDFSCluster`, `DistributedFileSystem`, `NameNode`, `Nfs3`, `RpcProgramNfs3`, `HdfsAdmin`, and privileged/unprivileged `SecurityHandler` mocks. `setup()` configures proxy-user impersonation, a Java key provider, ephemeral NFS ports, and `dfs.nfs.exports.allowed.hosts=* rw`; `createFiles()` resets `/tmp`, `/tmp/foo`, and `/tmp/bar` before each test. Each test serializes NFS request objects through `XDR` and calls the corresponding `nfsd` method directly: `getattr`, `setattr`, `lookup`, `access`, `readlink`, `read`, `write`, `create`, `mkdir`, `symlink`, `remove`, `rmdir`, `rename`, `readdir`, `readdirplus`, `fsstat`, `fsinfo`, `pathconf`, and `commit`.

## Control Flow
Most tests follow the same path: resolve a DFS file ID via `NameNode.getRpcServer().getFileInfo`, build a `FileHandle(fileId, namenodeId)`, serialize the request, call the NFS procedure once as user `harry` and once as the current system user, then assert `NFS3ERR_ACCES` for the first path and success or async-null for the second. `testEncryptedReadWrite()` creates an HDFS encryption zone, writes bytes through NFS using `WRITE3Request`, commits through `COMMIT3Request`, then compares NFS and DFS reads; it also verifies that a DFS-created encrypted file can be read through NFS. Helper methods `createFileUsingNfs`, `getFileContentsUsingNfs`, `getFileContentsUsingDfs`, and `commit` encapsulate that flow.

## State and Persistence Behavior
The tests mutate an in-process HDFS namespace, create a temporary Java keystore under the test root, and start NFS services on ephemeral ports. NFS write and commit paths may return `null` because the write manager replies asynchronously through Netty `Channel` callbacks. File handles encode HDFS inode/file IDs and namenode IDs, so the test explicitly couples NFS object identity to NameNode metadata.

## Dependencies and Integration Points
The class integrates HDFS mini-cluster services, key-provider/encryption-zone support, NFS request/response model classes, ONC RPC XDR serialization, Hadoop proxy-user authorization, and Mockito security identities. It also checks `NfsConfiguration` deprecation mappings from legacy keys such as `nfs3.server.port`, `dfs.nfs3.dump.dir`, and `hadoop.nfs.userupdate.milly` to the current constants.

## Risks and Test Signals
The fixture is broad and comparatively expensive because it starts a cluster and NFS service. It depends on local user identity, proxy-user refresh, and ephemeral port availability. Strong signals include positive/negative authorization checks across nearly every NFSv3 procedure, encrypted data integrity across DFS and NFS, read EOF validation, idempotency expectations for `NFSPROC3`, and deprecated-key compatibility. The class calls `RpcProgramNfs3` directly with serialized request buffers rather than testing network transport framing.
