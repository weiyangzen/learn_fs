# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/wsrs/TestJSONMapProvider.java

Purpose: Unit test for JAX-RS JSON writer provider for `Map` types.

Important APIs/types/functions: `JSONMapProvider.isWriteable`, `getSize`, and `writeTo`.

Control flow: asserts the provider is writable for `Map.class` but not the test class, reports unknown size as `-1`, writes a `JSONObject` containing `a=A`, and checks serialized JSON.

State and persistence: in-memory output stream only.

Dependencies/integration: JSON-simple, JAX-RS provider contract, and JUnit.

Risks and test signals: basic provider serialization guard. It does not verify media type handling, character encoding headers, nested maps, or read behavior.
