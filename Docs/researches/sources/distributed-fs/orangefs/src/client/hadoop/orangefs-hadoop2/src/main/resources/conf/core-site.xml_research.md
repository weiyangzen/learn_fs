<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/core-site.xml -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/core-site.xml

## Purpose

This `Hadoop 2/YARN` core-site file binds Hadoop's default filesystem to OrangeFS. It registers the `ofs` implementation class, maps the logical OrangeFS authority to a mounted OrangeFS path, and sets OrangeFS client buffer, block-size, and layout defaults used by the Java adapter.

## Important APIs, Types, and Functions

Important configuration keys are `fs.default.name`/`fs.defaultFS`, `fs.ofs.impl`, `fs.AbstractFileSystem.ofs.impl` for Hadoop 2, `fs.ofs.systems`, `fs.ofs.mntLocations`, `fs.ofs.file.buffer.size`, `fs.ofs.block.size`, and `fs.ofs.file.layout`.

Active properties observed:

- `fs.default.name` = `ofs://localhost-orangefs:3334`
- `fs.ofs.impl` = `org.apache.hadoop.fs.ofs.OrangeFileSystem`
- `hadoop.tmp.dir` = `/tmp/hadoop-${user.name}`
- `fs.defaultFS` = `ofs://localhost-orangefs:3334`
- `fs.AbstractFileSystem.ofs.impl` = `org.apache.hadoop.fs.ofs.OrangeFs`
- `fs.ofs.systems` = `localhost-orangefs:3334`
- `fs.ofs.mntLocations` = `/mnt/orangefs`
- `fs.ofs.file.buffer.size` = `4194304`
- `fs.ofs.block.size` = `134217728`
- `fs.ofs.file.layout` = `PVFS_SYS_LAYOUT_ROUND_ROBIN`
- `io.compression.codecs` = `org.apache.hadoop.io.compress.GzipCodec, org.apache.hadoop.io.compress.DefaultCodec, org.apache.hadoop.io.compress.BZip2Codec, org.apache.hadoop.io.compress.SnappyCodec`

## Control Flow

Hadoop loads this file from the configured `HADOOP_CONF_DIR` during daemon startup and client command execution. The values are consumed by Hadoop configuration lookup APIs before the OrangeFS `FileSystem` is initialized, so incorrect authority, mount-location, scheduler, or staging values surface as startup failures or runtime file-operation failures.

## State, Persistence, and Concurrency

The file is declarative configuration. It does not persist runtime state, but it points Hadoop at persistent OrangeFS storage paths and local temporary/log directories. Changes take effect only after affected daemons or client commands reload the configuration.

## Dependencies and Integration Points

It integrates Hadoop daemons, command-line examples, and the OrangeFS Java adapter. Values such as `ofs://localhost-orangefs:3334`, `/mnt/orangefs`, and `/tmp/orangefs_hadoop_storage` must match `orangefs-server.conf`, `pvfs2tab`, and the mounted OrangeFS client environment.

## Risks and Test Signals

Main risks are stale Hadoop-version keys, permissive ACL defaults, paths that do not exist on all nodes, and mismatched OrangeFS authorities or mount paths. Test by launching the matching Hadoop example stack, running `hadoop fs -ls ofs://localhost-orangefs:3334/`, and executing the included MapReduce examples; scheduler or staging mistakes usually appear before job tasks start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/main/resources/conf/core-site.xml -->
