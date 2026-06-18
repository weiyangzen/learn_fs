# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/wsrs/TestInputStreamEntity.java

Purpose: Unit test for `InputStreamEntity` streaming response entity.

Important APIs/types/functions: constructor `InputStreamEntity(InputStream)` and ranged constructor `InputStreamEntity(InputStream, offset, len)`, plus `write(OutputStream)`.

Control flow: first writes a full `ByteArrayInputStream("abc")` and asserts full output. Second writes with offset 1 and length 1 and asserts only byte `b` is emitted.

State and persistence: in-memory streams only.

Dependencies/integration: JUnit and Java IO. It validates behavior used by REST responses that stream file content or ranges.

Risks and test signals: narrow signal for basic full/range streaming. It does not cover zero-length, overrun, close propagation, or large stream behavior.
