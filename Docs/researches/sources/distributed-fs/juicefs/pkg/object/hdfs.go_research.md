# sources/distributed-fs/juicefs/pkg/object/hdfs.go


Purpose: implements HDFS storage behind `!nohdfs`, registering `hdfs`.

Important APIs and flow: `hdfsclient` wraps `colinmarc/hdfs` with address, base path, replication, umask, and close retry timings. `path` joins base path and key. `Head` maps HDFS `FileInfo` to JuiceFS `file`, normalizing HDFS superuser/group to root and sticky bit representation. `Get` returns empty for directories/out-of-range offsets or a section reader for ranges. `Put` creates temp files unless `PutInplace`, creates parents, handles existing temp paths, writes with `bufPool`, retries `Close` while HDFS reports replication in progress, then renames. `List` implements delimiter `/` sorted by path. `Chtimes`, `Chmod`, and `Chown` map to HDFS operations.

State and persistence: persistent state is HDFS files and directories under `basePath`. Temporary `.jfs.*` files may exist during writes.

Dependencies and integration: uses Hadoop configuration loading, optional Kerberos client, shared `FileSystem`, `SectionReaderCloser`, and `TmpFilePath`. `parseHDFSAddr` supports namenode HA nameservices from Hadoop config.

Risks: context parameters are not passed to the HDFS client. `Chtimes` updates atime too, noted by a FIXME. Close retry may delay writes for up to configured timeouts. User/group mapping is environment-sensitive.

Test signals: `TestHDFS` validates address parsing unconditionally, then runs storage tests only with `HDFS_ADDR`; `TestHDFS2` runs filesystem tests when configured.
