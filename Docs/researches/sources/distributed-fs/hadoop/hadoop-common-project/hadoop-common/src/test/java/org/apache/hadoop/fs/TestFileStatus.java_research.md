## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileStatus.java

Purpose: verifies `FileStatus` constructors, Writable serialization, Java serialization, equality/ordering semantics, symlink fields, default values, and exact `toString` formatting.

Important APIs/types/functions: `FileStatus`, `Path`, `FsPermission`, `Writable.write/readFields`, `ObjectOutputStream/ObjectInputStream`, `compareTo`, `equals`, and helpers `validateAccessors`/`validateToString`.

Control flow: tests write multiple `FileStatus` instances to a byte array and read them back; exercise full, no-symlink, no-owner, and blank constructors; assert equality depends on path rather than metadata; check ordering by path; validate `toString` for files, directories, and symlinks; and serialize/deserialize a status through Java object serialization.

State and persistence: all state is in memory. No filesystem calls are made beyond constructing `Path` values.

Dependencies/integration points: protects binary compatibility for Hadoop Writable serialization and Java serialization, plus user-visible string formatting consumed by logs/tools. It also documents defaults for owner/group/permission when omitted.

Risks and test signals: exact string assertions make intended output changes noisy but catch accidental regressions. Equality-by-path is subtle and may surprise callers; this test preserves that contract. Serialization failures would be high impact for IPC and persisted metadata paths.
