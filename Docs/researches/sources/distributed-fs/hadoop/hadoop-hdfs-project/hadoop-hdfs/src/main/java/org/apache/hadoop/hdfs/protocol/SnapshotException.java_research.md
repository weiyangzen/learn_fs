# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotException.java

Purpose: Represents snapshot-related failures in HDFS namespace operations.

Important APIs and types: `SnapshotException` extends `IOException` and provides message, cause, and message-plus-cause constructors.

Control flow: No custom flow beyond exception construction.

State and persistence behavior: Carries exception message/cause/stack trace. No persistent state is changed.

Dependencies and integration points: Used by snapshot creation, deletion, rename, listing, and snapshot-diff paths to report invalid snapshot operations.

Risks: Because it is public-looking and not annotated private here, client compatibility of constructors and messages matters. Wrapped causes should be preserved for diagnosing namespace failures.

Test signals: Snapshot tests should assert this type for duplicate snapshots, invalid snapshot roots, deletion constraints, diff errors, and cause-preserving constructor behavior.
