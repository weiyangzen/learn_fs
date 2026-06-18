<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestVersionedWritable.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestVersionedWritable.java

Purpose: JUnit coverage for Hadoop `VersionedWritable` serialization, inheritance, nested writable payloads, and version mismatch handling. The file defines local `VersionedWritable` fixtures and verifies that version bytes written by `VersionedWritable.write()` are enforced by `VersionedWritable.readFields()`.

Important APIs/types/functions: `SimpleVersionedWritable` extends `VersionedWritable` with random `int state`, static `VERSION = 1`, `write`, `readFields`, `read`, and `equals`. `AdvancedVersionedWritable` extends the simple fixture and adds UTF strings, `WritableUtils.writeString`, `writeCompressedString`, nested `SimpleVersionedWritable`, and string-array serialization. `SimpleVersionedWritableV2` overrides `getVersion()` to return `2`. Tests call `TestWritable.testWritable(...)` for round trips and `testVersionedWritable(before, after)` for mismatch assertions.

Control flow: round-trip tests serialize a fixture into `DataOutputBuffer`, reset a `DataInputBuffer` over the bytes, instantiate the same type through `ReflectionUtils` indirectly via `TestWritable`, and compare equality. The mismatch test serializes a V1 object, attempts to read it into a V2 object, expects `VersionMismatchException`, and fails if no exception is thrown.

State and persistence behavior: all state is in-memory test fixture state. Serialized format is version byte, then fixture fields. The advanced fixture persists multiple string encodings and a nested writable in sequence; ordering must match exactly on read. The random fields make object contents unpredictable but same-object round trip remains deterministic.

Dependencies and integration points: integrates with `VersionedWritable`, `VersionMismatchException`, `DataOutputBuffer`, `DataInputBuffer`, `WritableUtils`, and `TestWritable.testWritable`. It exercises Hadoop's binary Writable contract rather than filesystem or service state.

Risks and edge cases: `AdvancedVersionedWritable.equals()` calls `super.equals(o)` but ignores its return value, so a mismatch in inherited `state` would not fail equality if all subclass fields match. Tests print compression details to stdout. Because fixture version fields are static and mutable package-private/private, future tests that modify them could cross-contaminate if added.

Test signals: `testSimpleVersionedWritable` and `testAdvancedVersionedWritable` validate compatible serialization. `testSimpleVersionedWritableMismatch` validates exception behavior for incompatible versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestVersionedWritable.java -->
