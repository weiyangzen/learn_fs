# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/VersionedWritable.java

## Purpose

`VersionedWritable.java` is a base class for writable records with a leading version byte. Subclasses can evolve their payloads while checking compatibility during deserialization.

## Important APIs, types, and functions

- `getVersion()` is abstract and returns the current implementation version byte.
- `write(DataOutput)` writes the version byte.
- `readFields(DataInput)` reads a version byte and throws `VersionMismatchException` if it differs from `getVersion()`.

## Control flow

Subclasses normally call `super.write(out)` before writing their own fields and `super.readFields(in)` before reading the rest of their payload. If versions differ, `readFields()` throws before subclass fields are read.

## State and persistence behavior

The base class has no fields. Persisted state is one leading byte supplied by `getVersion()`. Subclasses define all subsequent persisted fields and may catch `VersionMismatchException` if they implement migration logic.

## Dependencies and integration points

It depends on `Writable`, `DataInput`, `DataOutput`, and `VersionMismatchException`. It is a simple compatibility hook for Hadoop IO types that predate richer schema evolution systems.

## Risks and edge cases

- Only exact version equality is accepted by the base implementation; compatible older versions require subclass override or exception handling.
- A single signed byte limits version representation and can display awkwardly above 127.
- Forgetting to call `super.write()` or `super.readFields()` breaks the format contract silently.

## Test signals

Tests should define a small subclass, assert version byte round-trip, mismatch exception behavior, and subclass payload read/write ordering around the superclass calls.
