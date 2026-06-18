<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/DFSClientCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/DFSClientCache.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/DFSClientCache.java` caches `DFSClient` and `FSDataInputStream` instances for NFS gateway users and namenodes. The source was read as a complete 357-line file for this report.

## Important APIs, Types, and Functions

Important types are private cache keys `DfsClientKey` and `DFSInputStreamCacheKey`, constructor, `prepareAddressMap`, `closeAll`, `clientLoader`, `getUserGroupInformation`, removal listeners, `inputStreamLoader`, `getDfsClient`, `getDfsInputStream`, and `invalidateDfsInputStream`. It uses Guava `LoadingCache` with max sizes 256 clients and 1024 input streams, and input streams expire after 10 minutes of access inactivity.

## Control Flow

Startup resolves configured export paths to HDFS URIs and builds `namenodeUriMap`, rejecting real namenode-ID collisions. Cache misses create proxy UGI for the effective user, relogin the real user from keytab if needed, and construct a `DFSClient` to the mapped namenode. Input-stream cache misses open a DFS input stream and wrap it. Removal listeners close clients and streams.

## State and Persistence Behavior

The caches are long-lived process memory. Shutdown hook `CacheFinalizer` closes cached clients. HDFS state is not persisted here, but cached clients and streams hold remote resources until eviction, invalidation, or shutdown.

## Dependencies and Integration Points

It integrates HDFS `DFSClient`, Hadoop `FileSystem`, UGI proxy users, `ShutdownHookManager`, `MultipleIOException`, shaded Guava caches, and `Nfs3Utils` namenode/export resolution.

## Risks and Edge Cases

`getDfsClient` and `getDfsInputStream` return null after loader failures, so callers must guard. Cache sizing and TTL affect resource pressure. Namenode ID hash collisions are explicitly detected only when authorities differ.

## Test Signals

`TestDFSClientCache`, `TestViewfsWithNfs3`, export collision tests, cache eviction/close tests, and Kerberos/proxy-user tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/DFSClientCache.java -->
