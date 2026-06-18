# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/CodecRegistry.java

Purpose: singleton registry mapping erasure codec names to ordered `RawErasureCoderFactory` implementations discovered through `ServiceLoader`.

Important APIs and control flow: constructor loads `RawErasureCoderFactory` providers and calls `updateCoders()`. `updateCoders()` groups factories by codec, rejects duplicate coder names, inserts native RS/XOR factories at the front as defaults, and rebuilds coder-name arrays plus compact comma-separated maps. Public methods expose coder names, factories, codec names, lookup by codec/coder name, and compact codec-to-coder map.

State and persistence: singleton `instance` holds mutable maps in memory. No disk persistence; provider availability depends on classpath service metadata.

Dependencies and integration: depends on raw coder factory classes, Java `ServiceLoader`, and Hadoop testing annotation. Used by `CodecUtil` to select raw encoder/decoder factories.

Risks and test signals: test duplicate coder registration, native factory precedence, empty/missing codec behavior, and compact map freshness. `getCoderByName()` assumes `getCoders()` is non-null; callers must check codec availability.
