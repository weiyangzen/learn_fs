<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/AbstractMapWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/AbstractMapWritable.java

Purpose: abstract base for `MapWritable` and `SortedMapWritable` class-id serialization. It stores per-instance mappings from writable classes to compact byte identifiers so nested maps can carry their own type tables.

Important APIs, types, and functions: predefined negative IDs cover common Hadoop writables. `addToMap(Class, byte)` and `addToMap(Class)` register classes. `getClass(byte)` and `getId(Class)` resolve mappings. `copy(Writable)` round-trips through `DataOutputBuffer`/`DataInputBuffer`. `write()` serializes new class mappings; `readFields()` loads them with the thread context class loader. It also implements `Configurable`.

Control flow: subclasses write this class table before their map entries, then use ids to encode key/value classes. Reads restore the table before entries are read.

State and persistence: instance state includes concurrent class/id maps, volatile count of new classes, and atomic configuration reference. Serialized persistence is the class table followed by subclass data.

Dependencies and integration points: used by Hadoop writable map implementations, `WritableFactories`, and configuration-aware serializers.

Risks and test signals: only 127 positive dynamic classes are allowed per instance. Loading arbitrary serialized class names depends on classpath and context class loader. Tests should cover duplicate id/class rejection, dynamic class limits, copy constructors, nested maps, missing class failures, and wire compatibility of predefined ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/AbstractMapWritable.java -->
