# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/fs/HdfsBlockLocation.java

Purpose: `BlockLocation` wrapper that carries the underlying HDFS `LocatedBlock` for clients that need HDFS-specific block detail.

Important APIs and functions: constructor copies a `BlockLocation` and stores a transient `LocatedBlock`; `getLocatedBlock()` exposes it; custom `readObject()` clears the transient block after deserialization; `isStriped()` delegates to `block.isStriped()`.

Control flow and state: serialization restores only the base `BlockLocation` state and sets `block` to null because `LocatedBlock` is not serializable.

Dependencies and integration: integrates common filesystem block location APIs with HDFS protocol block metadata.

Risks and test signals: after deserialization, `getLocatedBlock()` returns null and `isStriped()` will throw a null dereference. Callers need to avoid `isStriped()` on deserialized instances or the method needs defensive behavior elsewhere. FindBugs suppressions mention transient field restoration for related block location status classes.
