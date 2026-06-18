# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/web/TestFSMainOperationsWebHdfs.java

Purpose: runs core `FSMainOperationsBaseTest` behavior through `WebHdfsFileSystem` and adds WebHDFS-specific operation tests.

Important APIs/types/functions: `MiniDFSCluster`, `WebHdfsTestUtil`, `FSMainOperationsBaseTest`, `concat`, `truncate`, `WebHdfsFileSystem.jsonParse`, `GetOpParam.Op.GETHOMEDIRECTORY`.

Control flow: a static cluster with two datanodes is started, root permissions are opened, and a non-superuser WebHDFS filesystem is created through UGI. `testConcat` creates three source files and one target, concatenates, verifies sources disappear and length grows. `testTruncate` truncates a two-block file to one block, checks content and space consumed. `testJsonParseClosesInputStream` spies an HTTP connection so `jsonParse` reads a wrapper stream and verifies it closes. The mkdirs override verifies that creating subdirectories below a file fails and leaves no visible subdirectory.

State and persistence behavior: static MiniDFSCluster, files under `/test/hadoop`, root permission mutation, non-superuser working directory. Cluster is shut down after all tests.

Dependencies and integration points: integrates WebHDFS client, NameNode HTTP endpoint, DFS permissions, content summary, append/truncate semantics, and HTTP connection handling.

Risks: shared static filesystem and mutable `closedInputStream` field may couple tests if failures leave state. Non-superuser behavior depends on root permission setup.

Test signals: file concat/truncate correctness, stream cleanup for connection reuse, and HDFS-specific mkdir failure semantics.
