# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/FileSystemStatisticNames.java

Purpose: public constants for filesystem-level duration statistic names.

Important APIs and types: final utility class with private constructor and constants `FILESYSTEM_INITIALIZATION` and `FILESYSTEM_CLOSE`.

Control flow: no runtime logic beyond class loading.

State and persistence: immutable string constants; no mutation.

Dependencies and integration: used by filesystem implementations and statistics consumers to agree on key names for initialization and close durations.

Risks: changing constant values would break metric compatibility. The class intentionally has a small scope and does not enumerate stream/store statistics.

Test signals: compile-time use, constant value stability, private constructor coverage only if enforcing utility-class conventions.
