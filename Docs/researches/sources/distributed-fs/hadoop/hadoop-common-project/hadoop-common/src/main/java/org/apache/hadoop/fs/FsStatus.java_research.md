# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FsStatus.java

Purpose: `FsStatus` is a stable writable value object representing filesystem capacity, used bytes, and remaining bytes.

Important APIs: constructor, `getCapacity`, `getUsed`, `getRemaining`, `write`, and `readFields`.

Control flow and state: it stores three longs and serializes them in fixed order. `readFields` mutates an existing object from a `DataInput`; there is no validation on negative or inconsistent values.

Dependencies and integration: returned by `FileSystem.getStatus`/`AbstractFileSystem.getFsStatus` and serialized through Hadoop `Writable` pathways.

Risks: callers must interpret values from the filesystem correctly; this class does not enforce `capacity == used + remaining` or non-negative numbers. Writable field order is a compatibility contract.

Test signals: writable round-trip, large long values, zero/negative edge inputs if upstream permits them, and integration with `df`/status shell commands.
