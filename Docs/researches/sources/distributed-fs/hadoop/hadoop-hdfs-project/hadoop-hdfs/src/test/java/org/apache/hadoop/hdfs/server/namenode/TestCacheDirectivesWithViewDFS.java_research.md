# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCacheDirectivesWithViewDFS.java

## Purpose

`TestCacheDirectivesWithViewDFS` reruns the `TestCacheDirectives` suite through `ViewDistributedFileSystem` to verify cache-directive and cache-pool behavior works when HDFS is accessed through ViewDFS link and fallback configuration.

## Important APIs, Types, and Functions

The class extends `TestCacheDirectives` and overrides `getDFS()` and `getDFS(MiniDFSCluster, int)`. It sets `fs.hdfs.impl` to `ViewDistributedFileSystem`, reads the default HDFS URI from `CommonConfigurationKeys.FS_DEFAULT_NAME_KEY` or `cluster.getURI(0)`, and configures ViewFS with `ConfigUtil.addLinkFallback` plus an explicit `/tmp` link.

## Control Flow

The inherited base setup calls `getDFS`, so this subclass injects ViewDFS configuration before returning the filesystem. For HA/restart helper use, the cluster-indexed override updates the NameNode-specific configuration and returns `cluster.getFileSystem(0)` after setting ViewDFS mappings. All actual test methods, waits, and assertions are inherited from `TestCacheDirectives`.

## State and Persistence Behavior

No new persistence is introduced beyond the base cache-directives suite. The additional state is configuration-level ViewDFS mount/fallback mapping that rewrites how client paths reach the underlying HDFS namespace. Cache pool/directive state, stats, cached blocks, checkpoints, and HA expiry behavior remain stored in the underlying NameNode cache manager.

## Dependencies and Integration Points

The subclass integrates ViewDFS path resolution with `DistributedFileSystem` cache APIs, ViewFS fallback links, explicit `/tmp` mount links, MiniDFSCluster configuration, and all inherited NameNode cache-manager RPC paths.

## Risks and Edge Cases

Because it inherits a broad suite, failures may stem from ViewDFS path qualification rather than cache-manager logic. The overrides mutate shared configuration keys, so ordering with other tests using the same configuration object matters. The explicit `/tmp` link plus fallback covers common path resolution but does not test multiple mount tables or non-default nameservices.

## Test Signals

The signal is successful execution of the inherited `TestCacheDirectives` methods using ViewDFS-configured clients. In particular, relative path qualification, directive path listing, HA expiry consistency, and checkpoint/restart cache-manager state must behave identically to direct HDFS access.
