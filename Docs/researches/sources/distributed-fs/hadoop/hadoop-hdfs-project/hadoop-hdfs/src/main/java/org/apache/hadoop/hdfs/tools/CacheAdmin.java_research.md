<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/CacheAdmin.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/CacheAdmin.java

## Purpose

`CacheAdmin` implements the `hdfs cacheadmin` CLI for managing HDFS cache directives and cache pools.

## Important APIs and types

The tool extends `Configured` and implements `Tool`. Command classes implement `AdminHelper.Command`: `-addDirective`, `-modifyDirective`, `-listDirectives`, `-removeDirective`, `-removeDirectives`, `-addPool`, `-modifyPool`, `-removePool`, and `-listPools`. It uses `CacheDirectiveInfo`, `CacheDirectiveEntry`, `CacheDirectiveStats`, `CachePoolInfo`, `CachePoolEntry`, `CachePoolStats`, `CacheFlag.FORCE`, `FsPermission`, `RemoteIterator`, and `TableListing`.

## Control flow

`run` validates the first argument, dispatches to a command, and converts `IllegalArgumentException` to exit `-1`. Directive commands parse options, validate required IDs/paths/pools, build `CacheDirectiveInfo`, optionally set `FORCE`, and call `DistributedFileSystem` cache APIs. Listing commands stream remote iterators into tables and optionally add stats. Pool commands parse owner/group/mode/limit/default replication/max TTL, build `CachePoolInfo`, and call add/modify/remove/list APIs.

## State and persistence behavior

The CLI itself is stateless. It mutates persistent NameNode cache metadata: directives, pools, permissions, limits, TTLs, and default replication. Listing reads current NameNode cache manager state.

## Dependencies and integration points

It depends on `AdminHelper`, `DistributedFileSystem`, HDFS protocol cache classes, Hadoop CLI `ToolRunner`, `StringUtils` option parsing, Commons `WordUtils`, shaded Guava `Joiner`, and `TableListing`.

## Risks and test signals

Risks include partial success in `-removeDirectives`, insufficient numeric validation for replication/default replication, octal mode parsing errors, path URI selection for ViewFS or federated paths, and list output compatibility. Tests should cover every command's required/unknown arguments, success and NameNode failure exit codes, "never"/"unlimited" parsing, `-force` propagation, stats output, and partial deletion failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/CacheAdmin.java -->
