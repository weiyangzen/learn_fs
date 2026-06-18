<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayWritable.java

Purpose: writable wrapper for homogeneous arrays of `Writable` objects.

Important APIs, types, and functions: constructors set a non-null `valueClass` and optional values. `toStrings()` maps each value to `toString()`. `toArray()` returns a shallow copy of the writable array. `set()` and `get()` manage the value array. `readFields()` reads an int length, instantiates each element with `WritableFactories.newInstance(valueClass)`, and reads it. `write()` writes length and each element.

Control flow: serialization and deserialization are sequential and depend on all elements sharing the declared class.

State and persistence: state is the declared value class and writable array. Serialized form omits the value class, so readers must be constructed with the correct class.

Dependencies and integration points: used by MapReduce and writable serialization APIs; string constructor uses deprecated `UTF8` values under `Text.class`.

Risks and test signals: `values` can be null until set, causing write/toStrings failures. Serialized data cannot self-describe element type. Tests should cover read/write round trips, subclass constructors for reducer use, empty arrays, null value arrays, shallow copy behavior, and factory configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayWritable.java -->
