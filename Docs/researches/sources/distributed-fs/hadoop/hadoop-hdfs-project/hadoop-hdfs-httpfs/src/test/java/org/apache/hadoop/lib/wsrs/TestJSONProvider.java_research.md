# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/wsrs/TestJSONProvider.java

Purpose: Unit test for JAX-RS JSON writer provider for `JSONObject`.

Important APIs/types/functions: `JSONProvider.isWriteable`, `getSize`, and `writeTo`.

Control flow: asserts writability for `JSONObject.class`, non-writability for the test class, unknown size `-1`, and exact serialization of a simple object.

State and persistence: in-memory output stream only.

Dependencies/integration: JSON-simple, JAX-RS provider contract, and JUnit.

Risks and test signals: basic JSON entity writer signal. It does not cover arrays, non-ASCII, media type selection, or error handling during write.
