# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/DeprecatedUTF8.java

Purpose: Wraps the deprecated `org.apache.hadoop.io.UTF8` class so HDFS code can keep using legacy UTF8 serialization without local `@SuppressWarnings("deprecation")` annotations at each call site. It is a compatibility shim for old wire/storage formats.

Important APIs and types: `DeprecatedUTF8` extends `UTF8` and provides default, `String`, and copy constructors. Static `readString(DataInput)` and `writeString(DataOutput, String)` delegate directly to the deprecated `UTF8` string helpers.

Control flow: There is no independent logic. Construction and serialization flow immediately through the superclass or static `UTF8` methods.

State and persistence behavior: Instances inherit mutable string/byte state from `UTF8`. The static helpers read and write legacy UTF8-encoded values to Hadoop `DataInput`/`DataOutput`, so the persistence behavior is exactly the deprecated Hadoop UTF8 format.

Dependencies and integration points: Depends on Hadoop `UTF8` and Java data streams. It is intended for package-internal HDFS code that must read old edit/fsimage or protocol encodings.

Risks: Keeping the wrapper can hide continued dependence on a deprecated encoding. Any behavior differences, size limits, or malformed input handling come from `UTF8`. Replacing it with standard UTF-8 requires compatibility checks for persisted data.

Test signals: Serialization compatibility tests should compare bytes produced by `DeprecatedUTF8.writeString` and `UTF8.writeString`, read legacy strings from historical images/edits, and compile with deprecation warnings suppressed only inside this class.
