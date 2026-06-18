<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayPrimitiveWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayPrimitiveWritable.java

Purpose: writable wrapper for primitive Java arrays with a compact per-element binary representation and no object allocation per element.

Important APIs, types, and functions: constructors optionally declare a required component type. `set(Object)` validates non-null primitive arrays and stores the original array without copying. `write()` writes the primitive component type name through deprecated UTF8, writes length, then writes elements using type-specific loops. `readFields()` reads type and length, validates declared type, allocates a primitive array, and fills it. Nested `Internal` is used by `ObjectWritable`.

Control flow: serialization selects the primitive branch once, then loops over array elements. Deserialization mirrors the branch after allocating an array with `Array.newInstance()`.

State and persistence: state includes component type, optional declared component type, length, and the backing primitive array. Serialized form is type name, int length, and raw primitive values.

Dependencies and integration points: used by `ObjectWritable` for primitive array transport and depends on Hadoop exception types and legacy UTF8 string helpers.

Risks and test signals: constructor and `set()` alias the caller's array, so later mutations affect serialized output. Negative lengths are rejected, but very large lengths can allocate large arrays. Tests should cover all primitive types, declared-type enforcement, null/non-array/object-array rejection, negative length rejection, aliasing behavior, and ObjectWritable interop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/ArrayPrimitiveWritable.java -->
