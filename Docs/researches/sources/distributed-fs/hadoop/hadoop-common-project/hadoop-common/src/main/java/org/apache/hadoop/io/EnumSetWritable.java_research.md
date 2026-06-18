<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/EnumSetWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/EnumSetWritable.java

Purpose: writable wrapper around `EnumSet` that preserves enum element type even for null or empty sets.

Important APIs, types, and functions: constructors and `set(EnumSet,EClass)` validate that null/empty values have an element type. Collection methods delegate to the underlying set. `write()` writes -1 for null, 0 for empty with class name, or count plus each enum via `ObjectWritable`. `readFields()` reconstructs null, empty, or populated sets using configuration-aware class loading. It implements `Configurable` and registers a `WritableFactory`.

Control flow: populated reads deserialize the first enum to create `EnumSet.of(first)`, then add remaining elements. Empty reads load the element class name and create `EnumSet.noneOf()`.

State and persistence: state is the enum set, transient element type, and transient configuration. Serialized form includes length and, when needed, element class or serialized enum elements.

Dependencies and integration points: depends on `ObjectWritable`, `WritableUtils`, configuration, and writable factories.

Risks and test signals: `write()` for null assumes `elementType` is non-null; `equals(null)` throws instead of returning false. Tests should cover null set with type, empty set with type, populated sets, config class loading, add-on-null behavior, equals/hash edge cases, and factory instantiation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/EnumSetWritable.java -->
