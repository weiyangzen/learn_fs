# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/statinfo.h

## Purpose
`StatInfo` represents HDFS file, directory, and symlink metadata returned by libhdfs++.

## Important APIs, Control Flow, and State
The struct includes file type enum values, path, full path, length, permissions, owner, group, modification/access times, symlink target, block replication, block size, file ID, and child count. The constructor initializes defaults in the implementation. `str()` formats in `hdfs_ls` style.

## Dependencies and Integration Points
It is used by `GetFileInfo`, `GetListing`, `Find`, tools like `find`, and C conversions to `hdfsFileInfo`.

## Risks and Test Signals
Metadata formatting, permissions width, time units, and file type mapping must match Hadoop expectations. Tests should cover all file types, empty owner/group, symlinks, directories with child counts, large file IDs/sizes, listing batches, and conversion to legacy C structs.
