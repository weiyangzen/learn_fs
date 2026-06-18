# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/SortedMapWritable.java

## Purpose

`SortedMapWritable.java` implements a writable `SortedMap` whose keys are `WritableComparable` and whose values are `Writable`. It extends `AbstractMapWritable` to serialize a compact class-id table before the map entries and uses a `TreeMap` for natural key ordering.

## Important APIs, types, and functions

- `SortedMapWritable<K extends WritableComparable<? super K>>` implements `SortedMap<K, Writable>`.
- Constructors initialize an empty `TreeMap` or copy another `SortedMapWritable`.
- Map and sorted-map methods delegate to `instance`: `firstKey`, `lastKey`, `headMap`, `tailMap`, `subMap`, `entrySet`, `keySet`, `values`, `put`, `putAll`, `remove`, `size`, and related queries.
- `put()` registers both key and value classes with `AbstractMapWritable.addToMap()`.
- `readFields()` reads the class-id table, entry count, then byte class ids and object payloads using `ReflectionUtils.newInstance()`.
- `write()` emits the class-id table, entry count, class ids, and serialized key/value payloads.

## Control flow

Writes first call `super.write(out)` so the class-id registry is persisted. They then write the number of entries and iterate in sorted-key order, writing one byte id plus object bytes for each key and value. Reads reverse the process: `super.readFields(in)` loads the registry, then the entry count drives a loop that instantiates key and value classes by id, calls `readFields()`, and inserts into the `TreeMap`.

## State and persistence behavior

The mutable state is the `TreeMap` plus class-id mappings inherited from `AbstractMapWritable`. Persisted data includes enough class metadata for heterogeneous writable values and keys, but ordering after read is determined by the natural ordering of key objects. The deserializer does not clear `instance` before loading entries, so reading into a reused object can retain preexisting entries if not cleared externally.

## Dependencies and integration points

This class depends on `AbstractMapWritable`, `Writable`, `WritableComparable`, `ReflectionUtils`, and Java `SortedMap`/`TreeMap`. It is the sorted variant of Hadoop map-writable containers and integrates with standard `Writable` serialization pipelines.

## Risks and edge cases

- `comparator()` always returns `null`, so custom comparators are not serialized or preserved.
- Reusing an object for `readFields()` without `clear()` can merge old and new state.
- `in.readInt()` entry count is not validated for negative or excessive values before looping.
- Class ids are bytes; correctness relies on `AbstractMapWritable` registry consistency.
- Mutating key objects after insertion can corrupt `TreeMap` ordering.

## Test signals

Tests should cover sorted iteration order, copy construction, heterogeneous writable values, class-id preservation across serialization, empty maps, equality/hash behavior, sub-map views, and read-into-reused-instance behavior. Negative or corrupted entry counts are useful fuzz cases.
