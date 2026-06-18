# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/test/java/org/apache/hadoop/hdfs/nfs/nfs3/TestViewfsWithNfs3.java

## Purpose
Integration tests for running Hadoop NFSv3 over `ViewFileSystem` with a federated `MiniDFSCluster`. The class validates that NFS exports, file handles, getattr/write routing, and rename semantics work when the visible namespace is composed from two underlying HDFS nameservices.

## Important APIs, Types, and Functions
`setup()` creates a two-nameservice `MiniDFSCluster` with `MiniDFSNNTopology.simpleFederatedTopology(2)`, obtains `hdfs1`, `hdfs2`, `nn1`, and `nn2`, configures `fs.defaultFS` to `viewfs:///`, and uses `ConfigUtil.addLink` to map `/hdfs1` to `/user1` and `/hdfs2` to `/user2`. It exports both viewfs paths via `NfsConfigKeys.DFS_NFS_EXPORT_POINT_KEY`, starts `Nfs3`, and captures `RpcProgramNfs3` plus `RpcProgramMountd`.

## Control Flow
The basic tests compare mountd export count with `viewFs.getChildFileSystems()`, verify viewfs path resolution against the backing HDFS paths, and compare `FileStatus` directory bits against each NameNode's `HdfsFileStatus`. The NFS access helpers build file handles using `Nfs3Utils.getNamenodeId(config, hdfsX.getUri())` and call `nfsd.getattr` or `nfsd.write`. Rename tests build source/destination directory handles for one or two namespaces and assert that cross-NameNode rename fails with `NFS3ERR_INVAL`, while same-NameNode rename succeeds and updates only the expected namespace.

## State and Persistence Behavior
The fixture persists temporary HDFS namespace entries in both federated namespaces for the duration of the class: base directories, files for access/write tests, and rename candidates. `viewFs` presents a synthetic namespace but the durable objects reside in `hdfs1` and `hdfs2`; NFS file handles carry the backing NameNode ID so routing depends on the handle, not just the path text.

## Dependencies and Integration Points
This class links HDFS federation, viewfs mount-table configuration, NFS export-point configuration, mountd export enumeration, XDR-serialized NFS requests, and router-like multi-NameNode file-handle lookup. It uses a mocked `SecurityHandler` for the current user and Hadoop proxy-user config to make direct NFS calls pass authorization.

## Risks and Test Signals
The main risk covered is accidental cross-namespace mutation through NFS rename; the expected behavior is explicit invalidation rather than cross-NameNode move. The tests depend on stable namenode-ID generation from configured URIs; mismatched URI normalization can cause `NFS3ERR_IO`. Signals include export count parity, viewfs-to-HDFS path resolution, metadata parity, successful NFS getattr/write to both nameservices, rejected wrong-namenode handles, rejected cross-NN rename, and successful single-NN rename.
