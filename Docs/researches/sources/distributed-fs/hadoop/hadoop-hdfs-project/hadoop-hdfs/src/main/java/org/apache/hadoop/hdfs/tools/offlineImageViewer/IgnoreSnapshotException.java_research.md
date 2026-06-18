## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/tools/offlineImageViewer/IgnoreSnapshotException.java

Purpose: `IgnoreSnapshotException` is a marker `IOException` used by offline image viewer components to signal intentionally ignored snapshot data.

Important APIs and control flow: the class has only a no-argument constructor and no additional fields or methods. Its value is its type identity, allowing callers to catch it separately from other `IOException` failures.

State, persistence, and dependencies: it has no state, persistence behavior, or non-JDK dependencies.

Integration points: it belongs to the offline image viewer package and is intended for code paths that choose to skip snapshot processing. In this subset, `ImageLoaderCurrent` handles snapshot structures directly and does not throw this exception.

Risks and test signals: tests should only need to verify catch behavior where other components use the marker. Because the exception carries no message or cause, diagnostic quality depends on the catch site. Future code using it should document whether ignoring snapshots is a normal mode or a degraded result.
