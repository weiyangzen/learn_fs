# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/Writable.java

## Purpose

`Writable.java` defines Hadoop's core binary serialization contract. Implementations write their fields to `DataOutput` and restore them from `DataInput`, usually reusing object storage for efficiency.

## Important APIs, types, and functions

- `write(DataOutput out)` serializes all fields.
- `readFields(DataInput in)` deserializes all fields into the current object.
- Javadoc documents the default-constructor pattern and optional static `read(DataInput)` factory convention.

## Control flow

The interface itself has no implementation. Serialization control flow is defined by each writable type, and callers must invoke methods in matching write/read order.

## State and persistence behavior

State is implementation-specific. The contract is positional binary persistence with no built-in schema, version, or class metadata. Object reuse during `readFields()` is encouraged.

## Dependencies and integration points

It depends only on Java `DataInput`, `DataOutput`, and `IOException`. It is the base contract for Hadoop MapReduce keys/values, sequence files, map files, object serialization helpers, and many IO utilities.

## Risks and edge cases

- Implementations must maintain exact read/write field ordering; there is no automatic validation.
- The interface has no default versioning or null handling.
- Reusing objects in `readFields()` can leave stale state if implementations forget to clear removed fields.
- Types used reflectively need accessible no-argument constructors even though the interface cannot enforce that.

## Test signals

Every writable implementation should have round-trip tests, compatibility fixtures for serialized bytes, corrupted/truncated input tests, and reuse tests that read multiple records into the same instance.
