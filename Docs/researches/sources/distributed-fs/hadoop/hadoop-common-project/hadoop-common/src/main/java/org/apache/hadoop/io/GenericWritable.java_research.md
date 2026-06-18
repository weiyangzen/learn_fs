<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/GenericWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/GenericWritable.java

Purpose: compact tagged-union wrapper for a fixed set of `Writable` implementation classes. It avoids writing a class name with every value by serializing a one-byte type index.

Important APIs, types, and functions: subclasses implement `getTypes()` with the allowed writable classes. `set(Writable)` records the instance and matching type index. `get()` returns the wrapped instance. `write()` writes the type byte then delegates to the instance. `readFields()` reads the unsigned type index, instantiates the registered class with `ReflectionUtils.newInstance(clazz, conf)`, and reads its fields. It implements `Configurable` so configuration reaches wrapped instances before deserialization.

Control flow: producers must call `set()` with a registered exact class before writing. Consumers must use the same `getTypes()` order to decode the type byte.

State and persistence: state is the type byte, wrapped instance, and configuration. Serialized form is one type byte plus the wrapped writable payload.

Dependencies and integration points: used when MapReduce sequence files need multiple value types under one declared value class.

Risks and test signals: only exact class equality is accepted, not subclasses. Type indexes are one byte, so practical type count is limited and ordering is a wire contract. `readFields()` does not validate bounds before indexing. Tests should cover each registered type, unregistered set failure, unset write failure, type-order compatibility, configuration propagation, and malformed type bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/GenericWritable.java -->
