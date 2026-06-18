<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSortedMapWritable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSortedMapWritable.java

## Purpose
Tests `SortedMapWritable` ordering, copy construction, nested maps, foreign class propagation, equality/hashCode contract, and class-map copying through `putAll`.

## Important APIs, Types, and Functions
Uses generic `SortedMapWritable<Text>`, `put`, `putAll`, copy constructor, `firstKey`, `lastKey`, `entrySet`, `keySet`, `getNewClasses`, `equals`, `hashCode`, and protected-ish class maps `classToIdMap`/`idToClassMap` visible from the package.

## Control Flow and State
The main test inserts three text keys, verifies first/last ordering, copies and compares values, then nests maps and verifies nested copy contents. `testForeignClass()` confirms deprecated `UTF8` registers one unknown class across copies. `testEqualsAndHashCode()` checks null inequality, empty equality, different entries, same entries inserted in different order, and same keys/different values. `testPutAll()` asserts entries and class metadata are copied.

## Dependencies and Integration Points
Protects sorted writable map serialization and class-id propagation, including legacy classes and nested map structures.

## Risks and Test Signals
Risks include generic unchecked casts, class metadata leakage, equality depending on sorted entry sets, and package-level class map assumptions. Signals are first/last keys, nested value comparisons, unknown class count, hash/equality contract checks, and class-map containment after `putAll`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestSortedMapWritable.java -->
