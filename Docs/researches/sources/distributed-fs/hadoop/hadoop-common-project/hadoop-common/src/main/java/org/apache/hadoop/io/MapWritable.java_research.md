# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/MapWritable.java

Purpose: `MapWritable` is a stable Writable `Map<Writable, Writable>` implementation that serializes heterogeneous Writable key and value classes by pairing map entries with class IDs maintained by `AbstractMapWritable`.

Important APIs and types: the class wraps a `HashMap<Writable, Writable>` and implements normal `Map` operations. `put` registers both key and value classes before insertion. `write` emits the superclass class table, entry count, then for each entry writes key class ID, key payload, value class ID, and value payload. `readFields` reads the class table, clears existing entries, instantiates key/value objects by ID via `ReflectionUtils`, reads their fields, and inserts them.

Control flow: mutations generally delegate to the backing map, with `put` and `putAll` adding class metadata. Serialization always starts with the class mapping inherited from `AbstractMapWritable`; deserialization rebuilds the mapping first, then reconstructs each object from class IDs embedded in the stream.

State and persistence: state includes the backing `HashMap` plus inherited class-ID mappings and optional configuration. Persistent representation is class mapping metadata followed by all entries in backing-map iteration order. Entry order is not stable because `HashMap` does not preserve order.

Dependencies and integration points: depends on `AbstractMapWritable`, `Writable`, `ReflectionUtils`, and Hadoop configuration propagation. It integrates with Hadoop RPC and serialization paths that need maps containing multiple Writable implementations.

Risks and test signals: risks include mutable Writable keys breaking hash lookups, nondeterministic serialized entry order, failure on unknown or non-instantiable classes, and class table drift if entries are mutated through collection views in ways that bypass `put`. Tests should cover heterogeneous round trips, copy construction, clearing before repeated reads, class registration through `putAll`, equality/hash behavior, and malformed class IDs.
