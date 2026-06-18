# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/TwoDArrayWritable.java

## Purpose

`TwoDArrayWritable.java` is a writable wrapper for a rectangular or ragged two-dimensional matrix of `Writable` values of one declared class.

## Important APIs, types, and functions

- Constructors take a `Class valueClass` and optionally a `Writable[][]`.
- `set()` and `get()` replace or return the internal matrix.
- `toArray()` builds a Java two-dimensional array with component type `valueClass` using reflection.
- `readFields()` reads row count, per-row lengths, instantiates values with `valueClass.newInstance()`, and reads each value.
- `write()` emits row count, row lengths, and each element payload.

## Control flow

Serialization writes matrix shape first so the reader can allocate all rows before reading cells. Deserialization constructs empty row arrays, then loops through every coordinate, creates a new `valueClass` instance, calls `readFields()`, and stores it. `toArray()` creates a two-dimensional reflective array whose first dimension is the row count and then replaces each row with an array sized to the corresponding row length.

## State and persistence behavior

State is the declared value class and mutable `Writable[][] values`. Persisted form stores no class name, so the reader must be constructed with the same `valueClass` used for writing. Ragged row lengths are preserved.

## Dependencies and integration points

The class depends on `Writable`, Java reflection `Array`, and the deprecated zero-argument `Class.newInstance()` pattern. It is a generic container for writable matrices in Hadoop serialization paths.

## Risks and edge cases

- There is no no-argument constructor, so frameworks must know the value class at construction time.
- Deserialization does not validate negative row counts or row lengths.
- `valueClass.newInstance()` requires an accessible no-argument constructor and wraps reflection failures as unchecked `RuntimeException`.
- Null `values`, null rows, or null cells cause `NullPointerException` during write or `toArray()`.
- The class stores raw `Class`, so type safety is runtime-only.

## Test signals

Tests should cover empty matrices, ragged matrices, round-trip with a simple writable, `toArray()` component type and row lengths, missing default constructor failures, null element failures, and corrupted negative dimensions.
