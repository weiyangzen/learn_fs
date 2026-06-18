# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/RecoveryInProgressException.java

Purpose: Signals that block replica recovery is already in progress. It lets callers distinguish concurrent recovery conflicts from generic IO failures.

Important APIs and types: `RecoveryInProgressException` extends `IOException` and exposes a single message constructor.

Control flow: No custom flow beyond exception construction.

State and persistence behavior: Exception state is the message and inherited stack trace. No persistent state is modified.

Dependencies and integration points: Used by HDFS block recovery paths where a second recovery attempt should be rejected or retried later.

Risks: Overusing generic `IOException` handling can hide the specific recovery-in-progress condition. Message quality matters for diagnostics.

Test signals: Tests should trigger concurrent replica recovery and assert this exception type is propagated or translated correctly to clients/callers.
