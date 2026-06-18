# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNameNodeRecovery.java

Purpose: Tests NameNode metadata recovery from edit logs containing padding, oversized operations, garbage, truncated tails, and finalized or in-progress corruption. The class is parameterized to run with synchronous and asynchronous edit log logging.

Important APIs and types: `runEditLogTest` drives low-level `EditLogFileOutputStream` and `EditLogFileInputStream` behavior using `nextOp` and `nextValidOp`. `EditLogTestSetup` describes edit log scenarios. Corruptors implement `Corruptor` with `TruncatingCorruptor`, `PaddingCorruptor`, and `SafePaddingCorruptor`. `testNameNodeRecoveryImpl` validates full cluster recovery with `StartupOption.RECOVER` and `MetaRecoveryContext.FORCE_ALL`.

Control flow: Low-level tests create a temporary edit log, write transaction records or raw bytes, flush and reopen the log, assert normal reading fails or succeeds at the expected transaction boundary, then use recovery-mode reads to skip bad regions. Full-cluster tests create directories, optionally prevent log finalization with a Mockito spy, corrupt the latest edits file, prove normal startup fails when recovery is required, run recovery startup, then restart normally and verify namespace contents survive.

State and persistence behavior: The target state is persisted edit-log data and NameNode storage directories. `setupRecoveryTestConf` creates HA-suffixed name and checkpoint directories to exercise generic key initialization. Recovery mutates on-disk edit logs so subsequent normal startup succeeds.

Dependencies and integration points: Uses MiniDFSCluster, FSImage, NNStorage, FSEditLog, edit log op classes, `DFSUtil.addKeySuffixes`, Apache commons file utilities, Mockito, and parameterized JUnit. It covers integration between edit log parsing, log segment finalization, recovery startup options, and namespace loading.

Risks: The tests rely on byte-level edit log formats and padding semantics; layout changes can require updates. Static `recoverStartOpt` and `EditLogFileOutputStream.setShouldSkipFsyncForTesting(true)` affect global test behavior. The async edit log parameter increases coverage but also sensitivity to flush/finalization behavior.

Test signals: Expected signals are correct last-valid transaction detection, `nextValidOp` recovering all intended transaction ids, normal startup rejection only when required, recovery startup completing without IOException, and post-recovery namespace paths still existing.
