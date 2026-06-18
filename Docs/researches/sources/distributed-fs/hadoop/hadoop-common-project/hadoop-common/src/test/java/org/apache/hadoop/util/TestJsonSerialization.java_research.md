# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/util/TestJsonSerialization.java

Purpose: validates `JsonSerialization<T>`, Hadoop's Jackson-backed helper for object JSON round trips across strings, bytes, local files, and Hadoop `FileSystem` APIs.

Important APIs and types: `JsonSerialization<KeyVal>`, `toJson`, `fromJson`, `toBytes`, `fromBytes`, `fromInstance`, `save`, `load`, `FileSystem`, `LocalFileSystem`, `FileStatus`, `PathIOException`, and `LambdaTestUtils`.

Control flow: tests round-trip a serializable `KeyVal` bean through JSON string, UTF-8 bytes, clone-via-JSON, plain `File`, and `FileSystem` paths. Negative tests feed bad bytes, empty local files, empty `Path` loads with and without status, and deleted paths to verify exception mapping.

State and persistence: persisted state is temporary JSON files in local filesystem storage. The bean's equality and hash code are used as the oracle after deserialization.

Dependencies and integration points: covers Jackson parser behavior, Hadoop local filesystem status APIs, file create/delete semantics, and wrapped filesystem exception contracts.

Risks: empty-file handling differs between direct file and FS-status load paths, parser exceptions can be wrapped differently, and overwrite flags matter. Test signals are exact equality checks and intercepted `JsonParseException`, `EOFException`, `PathIOException`, and `FileNotFoundException` outcomes.
