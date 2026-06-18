<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestGenericWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestGenericWritable.java

## Purpose
Tests `GenericWritable` wrapper behavior, type registration enforcement, and propagation of `Configuration` into wrapped configurable values.

## Important APIs, Types, and Functions
Defines dummy `Foo implements Writable`, `Bar implements Writable, Configurable`, `Baz extends Bar`, and `FooGenericWritable extends GenericWritable` with supported types `Foo`, `Bar`, and `Baz`. Uses `TestWritable.testWritable`, `setConf`, `set`, `get`, and equality overrides.

## Control Flow and State
`setUp()` creates a configuration with a sentinel key. `testFooWritable()` wraps a plain writable. `testBarWritable()` wraps a configurable writable and asserts the deserialized wrapped object has non-null conf. `testBazWritable()` asserts subclass deserialization sees the sentinel config during `readFields`. `testSet()` accepts registered `Foo` and rejects unregistered `IntWritable`. `testGet()` checks object retrieval.

## Dependencies and Integration Points
Integrates with Hadoop `Configurable`, `Configuration`, `Text` serialization, and shared `TestWritable` round-trip utilities. It protects polymorphic writable serialization used by RPCs and protocol containers.

## Risks and Test Signals
Risks are misordered type id mapping, missing configuration propagation before `readFields`, and weak equality/hash implementations in dummy types. Signals are round-trip equality, `Configurable` conf presence, sentinel config assertion, and runtime rejection of unregistered types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestGenericWritable.java -->
