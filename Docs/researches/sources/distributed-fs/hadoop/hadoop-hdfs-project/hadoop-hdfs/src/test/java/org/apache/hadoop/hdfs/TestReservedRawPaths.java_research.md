# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestReservedRawPaths.java

Purpose: tests the special `/.reserved/raw` namespace used to access encrypted HDFS data without decryption, plus path resolution, status/listing behavior, and access control around raw paths.

Important APIs and types: `MiniDFSCluster`, `HdfsAdmin`, `JavaKeyStoreProvider`, `CreateEncryptionZoneFlag.NO_TRASH`, `FSDirectory.resolvePath`, `INodesInPath`, `EncryptionZoneManager`, `FileSystemTestWrapper`, `FileContextTestWrapper`, `UserGroupInformation`, `AccessControlException`, and `DFSTestUtil.verifyFilesEqual/NotEqual`.

Control flow: setup configures a JKS key provider, starts a one-DN cluster, wires the client key provider to the NameNode provider, and creates an encryption key. Tests verify raw path resolution strips `/.reserved/raw` while setting `INodesInPath.isRaw`, raw encrypted bytes differ from decrypted EZ reads, raw non-EZ reads equal normal reads, status paths resolve to the same underlying inode, root and relative raw paths canonicalize, mkdir works as superuser through raw paths, non-admins can read/list but cannot create/mkdir raw paths, and `/.reserved` listing exposes `raw` and `.inodes` appropriately.

State and persistence behavior: creates encryption zones, encrypted and unencrypted files, permissions, and namespace entries. It does not restart the cluster, but it exercises raw path normalization against live FSDirectory state and key-provider-backed encryption metadata.

Dependencies and integration points: integrates HDFS encryption zones, raw reserved path resolver, FileSystem and FileContext wrappers, key provider flushing, permission checks, listing APIs, and FSDirectory constants.

Risks and edge cases: raw access is security-sensitive; tests distinguish read/list permissions from write/mkdir superuser requirements. Path construction includes unusual relative forms and a nested path under `/.reserved/raw` to catch normalization bugs. `assertPathEquals` uses access/modification times as inode identity proxies rather than comparing inode IDs directly.

Test signals: raw flag and resolved path values, byte equality/inequality, expected `AccessControlException` messages, `FileNotFoundException` for `/.reserved/.inodes`, listing names and recursive raw paths matching expected regexes.
