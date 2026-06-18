# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestStripedFileAppend.java

Purpose: Tests append behavior for erasure-coded striped files, including supported append-to-new-block behavior and unsupported append-without-new-block behavior.

Important APIs and types: `DistributedFileSystem.setErasureCodingPolicy`, `dfs.append` with `CreateFlag.APPEND` and `CreateFlag.NEW_BLOCK`, `LocatedBlocks`, `StripedFileTestUtil.verifyStatefulRead`, `verifySeek`, `RemoteIterator<OpenFileEntry>`, and `OpenFilesType.ALL_OPEN_FILES`.

Control flow: Each test creates a MiniDFSCluster with nine datanodes and block size derived from default EC policy cell size and stripes-per-block, creates `/TestFileAppendStriped`, and sets EC policy. `testAppendToNewBlock` writes six splits: first with create, subsequent with append plus NEW_BLOCK. Each split writes a random length less than one block group from a generated expected buffer, then closes. It asserts six located block groups and verifies reads/seeks. `testAppendWithoutNewBlock` writes a small EC file, attempts append without NEW_BLOCK, asserts the expected unsupported-operation message, then lists open files to ensure the failed append left no lease/open-file state.

State and persistence behavior: File data and EC block groups live in MiniDFSCluster for the test. The failed append test checks transient open-file state is cleaned up.

Dependencies and integration points: Integrates EC policy inheritance, DFS striped output, append flags, NameNode open-file tracking, located-block metadata, and striped read verification.

Risks and test signals: Random split lengths mean coverage varies while staying under block-group size. Passing signals append-to-new-block creates correct block groups and failed unsupported append does not leak open file handles.
