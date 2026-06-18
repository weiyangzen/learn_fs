# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/RpcProgramNfs3.java

## Purpose
`RpcProgramNfs3` is the Hadoop NFSv3 server-side RPC program. It implements `Nfs3Interface`, translates NFSv3 requests to HDFS `DFSClient` operations, enforces export and port access checks, manages metrics and duplicate-call caching, and delegates asynchronous write/commit work to `WriteManager`.

## Important APIs, Types, And Functions
The class exposes handlers for NFSv3 procedures: `getattr`, `setattr`, `lookup`, `access`, `readlink`, `read`, `write`, `create`, `mkdir`, `mknod`, `remove`, `rmdir`, `rename`, `symlink`, `link`, `readdir`, `readdirplus`, `fsstat`, `fsinfo`, `pathconf`, and `commit`. Lifecycle APIs are `createRpcProgramNfs3`, `startDaemons`, `stopDaemons`, `handleInternal`, `isIdempotent`, and test-visible accessors. Support methods include `setattrInternal`, `mapErrorStatus`, `listPaths`, `getSecurityHandler`, and `checkAccessPrivilege`.

## Control Flow
Construction configures umask, id mapping, exports, `WriteManager`, `DFSClientCache`, HDFS create defaults, dump directory cleanup, Kerberos login, superuser name, duplicate-call cache, and HTTP server. `startDaemons` starts the pause monitor, async write service, and info server; `stopDaemons` stops them.

`handleInternal` validates authentication flavor except for NULL, checks duplicate non-idempotent calls in `RpcCallCache`, dispatches by `NFSPROC3`, records metrics for synchronous procedures, serializes a response if one is returned, and sends it through Netty. `write` and `commit` usually return `null` because response delivery is handled asynchronously through `WriteManager` and `OpenFileCtx`.

Each handler deserializes its XDR request, obtains a user/namenode-specific `DFSClient` from `DFSClientCache`, checks export privilege through `NfsExports`, maps file handles to `.reserved/.inodes` paths via `Nfs3Utils`, performs HDFS operations, and builds NFS response plus weak-cache-consistency data where applicable.

## State And Persistence
Persistent filesystem effects are HDFS creates, deletes, renames, symlinks, attribute updates, appends, and syncs. In-memory state includes config, id mapper, client cache, export table, write manager, RPC call cache, metrics, pause monitor, info server, and dump directory path. Startup can delete and recreate the configured write dump directory when dump support is enabled.

## Dependencies And Integration Points
It depends on Hadoop HDFS client APIs, NFS protocol request/response classes, ONCRPC/Netty transport, `NfsExports`, `ShellBasedIdMapping`, `DFSClientCache`, `WriteManager`, `Nfs3HttpServer`, metrics, Kerberos/security utilities, and MiniDFS-backed tests. It is instantiated and hosted by `Nfs3`.

## Risks
The class is broad and security-sensitive. Export checks are separate from HDFS permission checks; missing either can expose operations. `getSecurityHandler` only builds handlers for AUTH_SYS and returns null otherwise, while `handleInternal` allows RPCSEC_GSS flavor through the initial check, so unsupported credential paths need care. READ retries are effectively once despite the comment. Directory cookies use HDFS file IDs and special dot handling to satisfy Linux clients; deleted-cookie recovery restarts listing from the beginning and can duplicate entries. Asynchronous write/commit responses must preserve xid/channel correctness and duplicate-call semantics.

## Test Signals
This subset covers startup and portmap timeout propagation (`TestMountd`), export privilege denial (`TestClientAccessPrivilege`), export-point validation (`TestExportsTable`), HTTP info server (`TestNfs3HttpServer`), directory listing cookies (`TestReaddir`), access-right utility behavior (`TestNfs3Utils`), and manual write/UDP harnesses. Broader regression signals are NFS gateway integration tests over MiniDFSCluster.
