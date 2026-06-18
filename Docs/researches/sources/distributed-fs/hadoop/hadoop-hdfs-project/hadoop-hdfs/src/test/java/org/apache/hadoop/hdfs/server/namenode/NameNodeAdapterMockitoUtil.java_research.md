<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NameNodeAdapterMockitoUtil.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NameNodeAdapterMockitoUtil.java

Purpose: Mockito-based companion utility for replacing selected NameNode internals with spies during tests.

Important APIs/types/functions: `spyOnBlockManager()`, `spyOnFsLock()`, `spyOnFsImage()`, `spyOnJournalSet()`, `spyOnNamesystem()`, `spyOnEditLog()`, and `spyDelayMkDirTransaction()` create spies and install them into the relevant production objects.

Control flow: each method spies the current internal object, then uses public testing setters, `DFSTestUtil`, `Whitebox`, or Apache Commons `FieldUtils` to update back-references. `spyOnNamesystem()` locks old and new namesystems while replacing `NameNode.namesystem` and related references in RPC server, block manager, lease manager, datanode manager, and heartbeat manager. `spyDelayMkDirTransaction()` intercepts `FSEditLogAsync.doEditTransaction()` only for `OP_MKDIR` and sleeps before delegating.

State and persistence: state changes are in-memory test substitutions. Edit-log and journal spies still wrap real persistent components, so intercepted calls can delay or observe real persistence without replacing behavior unless a test stubs it further.

Dependencies and integration points: depends on Mockito, `FieldUtils`, `Whitebox`, `DFSTestUtil`, `BlockManagerTestUtil`, and HA `EditLogTailer`.

Risks and test signals: risks are fragile private-field names and incomplete back-reference replacement causing mixed real/spy state. Test signals are successful verification/stubbing of NameNode internal calls, lock behavior, edit-log delays, and block-manager interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/NameNodeAdapterMockitoUtil.java -->
