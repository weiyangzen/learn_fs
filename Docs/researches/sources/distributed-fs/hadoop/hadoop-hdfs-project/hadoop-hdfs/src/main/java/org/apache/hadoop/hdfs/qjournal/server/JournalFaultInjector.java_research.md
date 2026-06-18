<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalFaultInjector.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalFaultInjector.java

Purpose: Test hook for injecting failures around Paxos recovery persistence in `Journal.acceptRecovery`.

Important APIs/types/functions: Static mutable `instance`, `get`, `beforePersistPaxosData`, and `afterPersistPaxosData`.

Control flow: Production methods are no-ops. Tests replace `instance` to throw before or after `persistPaxosData`, exercising the recovery operation's atomicity and roll-forward behavior.

State and persistence behavior: No production persistence. It targets the boundary between downloaded temporary edit files and persisted Paxos decision files.

Dependencies/integration: Called only by `Journal.acceptRecovery`; marked visible for testing and private audience.

Risks: Static global replacement can leak between tests if not reset. Production code assumes no-op behavior and does not guard against injected exceptions except through normal IO failure paths.

Test signals: Fault-injection tests should reset the singleton, fail before/after Paxos persistence, restart/reprepare the journal, and verify no externally visible partial recovery or data loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/qjournal/server/JournalFaultInjector.java -->
