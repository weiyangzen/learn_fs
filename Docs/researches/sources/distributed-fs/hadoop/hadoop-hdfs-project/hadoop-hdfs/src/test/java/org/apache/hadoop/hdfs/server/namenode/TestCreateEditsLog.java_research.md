# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestCreateEditsLog.java

Purpose: Verifies the `CreateEditsLog` utility emits edit logs that a NameNode can load successfully after being moved into a formatted name directory.

Important APIs/types/functions: Uses `DFSTestUtil.formatNameNode`, `CreateEditsLog.main`, local `FileContext` glob/rename, `MiniDFSCluster.Builder.format(false)`, and `manageNameDfsDirs(false)`.

Control flow: Deletes prior test directories, formats NameNode storage, runs `CreateEditsLog -f 1000 0 1 -d <testdir>`, moves generated edit files into `name/current`, then starts a MiniDFSCluster without reformatting.

State and persistence behavior: Persistent state is generated edits in local storage; the test proves serialized utility output is compatible with NameNode startup replay.

Dependencies and integration points: Connects an offline metadata-generation tool to real NameNode edit log loading and the `current` storage layout.

Risks: It does not inspect namespace contents after replay, only parse/load compatibility. Cleanup failures can pollute later runs.

Test signals: Successful NameNode startup and `waitClusterUp` with no exception.
