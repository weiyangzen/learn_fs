# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/statistics/IOStatisticsSupport.java

Purpose: public support helpers for snapshots, source retrieval, and no-op duration tracking.

Important APIs, types, and functions: `snapshotIOStatistics(IOStatistics)`, `snapshotIOStatistics()`, `retrieveIOStatistics(Object)`, `stubDurationTrackerFactory()`, and `stubDurationTracker()`.

Control flow: snapshot helpers instantiate `IOStatisticsSnapshot`; retrieval casts direct `IOStatistics` instances before asking `IOStatisticsSource` objects for their statistics. Stub helpers return singleton no-op tracker objects.

State and persistence: stateless. Snapshot helpers create serializable state in returned `IOStatisticsSnapshot` objects.

Dependencies and integration points: depends on public statistics interfaces and implementation stubs. It is used by logging, callers that accept optional statistics, and code paths where duration tracking must be optional.

Risks and test signals: retrieval returns null for null or non-statistics objects, so callers must not blindly dereference. Tests should cover direct statistics, source wrappers, null sources, unsupported sources, snapshot copy behavior, and singleton no-op duration trackers.
