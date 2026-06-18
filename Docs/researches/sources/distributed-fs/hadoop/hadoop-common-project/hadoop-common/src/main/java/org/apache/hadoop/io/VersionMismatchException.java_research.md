# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/VersionMismatchException.java

## Purpose

`VersionMismatchException.java` is the checked exception thrown when serialized data carries a version byte that does not match the current `VersionedWritable` implementation's expected version.

## Important APIs, types, and functions

- The class extends `IOException`.
- Constructor stores expected and found version bytes.
- `toString()` returns a human-readable mismatch message.

## Control flow

There is no complex control flow. `VersionedWritable.readFields()` and `SequenceFile.Reader` create this exception when they detect incompatible versions.

## State and persistence behavior

The exception stores two private bytes: `expectedVersion` and `foundVersion`. It is not itself a serialized data format, and it does not define `serialVersionUID`.

## Dependencies and integration points

The class depends on `IOException` and is referenced by `VersionedWritable` and sequence-file version checks. It is part of Hadoop IO's compatibility signaling.

## Risks and edge cases

- The constructor does not call `super(message)`, so `getMessage()` may be null even though `toString()` is informative.
- Stored bytes can display as signed values for versions above 127.
- There are no accessors for expected/found versions.

## Test signals

Tests should assert `toString()` content, behavior when caught as `IOException`, and callers' handling of mismatched version bytes.
