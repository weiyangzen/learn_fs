<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritableName.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritableName.java

Purpose: Unit coverage for `WritableName`, which maps short aliases to classes and resolves names with Hadoop serialization support.

Important APIs/types/functions: local `SimpleWritable` supplies a Writable target class. `SimpleSerializable` and `SimpleSerializer` provide a non-Writable class plus `Serialization` implementation. Tests exercise `WritableName.getClass`, `WritableName.setName`, `WritableName.addName`, and `SerializationFactory.getSerialization`.

Control flow: `testGoodName` resolves built-in alias `"long"`. `testSetName` assigns a canonical test alias to `SimpleWritable` and resolves it. `testAddName` adds an alternate alias while checking the original alias still works. `testAddNameSerializable` configures `io.serializations`, adds an alias for a serializable non-Writable type, and verifies `SerializationFactory` can resolve it both by alias and class name. `testBadName` expects an `IOException` mentioning the unknown name.

State and persistence behavior: alias mappings are process-local static state inside `WritableName`. There is no filesystem persistence; only `Configuration` controls serialization class discovery.

Dependencies and integration points: depends on `CommonConfigurationKeys.IO_SERIALIZATIONS_KEY`, `SerializationFactory`, `Serialization`, and `WritableName`. It validates that Writable-style aliases and generic serialization lookup coexist.

Risks and edge cases: static alias registration can leak between tests if names collide. The custom serializer returns null serializer/deserializer because only serializer discovery is tested. `assertTrue(false)` is used instead of `fail`.

Test signals: verifies built-in alias lookup, explicit name setting, alternate aliases, serializable class aliasing, and useful exception messages for missing names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritableName.java -->
