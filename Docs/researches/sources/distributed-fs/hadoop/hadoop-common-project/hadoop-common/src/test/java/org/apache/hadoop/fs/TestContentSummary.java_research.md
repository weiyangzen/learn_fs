# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestContentSummary.java

## Purpose
`TestContentSummary` validates the `ContentSummary` value object. It checks builder defaults, quota and non-quota construction, writable serialization order, deserialization, formatted headers, standard string formatting, human-readable formatting, and snapshot formatting.

## Important APIs, Types, And Functions
The tests use `ContentSummary.Builder`, getters for length/file count/directory count/quota/space consumed/space quota, `write(DataOutput)`, `readFields(DataInput)`, `ContentSummary.getHeader(boolean)`, `toString(boolean)`, `toString()`, `toString(boolean, boolean)`, and `toSnapshot(boolean)`. Mockito `mock()`, `when()`, `inOrder()`, and `InOrder` validate serialization and deserialization.

## Control Flow
Constructor tests build empty, quota-filled, and no-quota summaries and assert field values. `testWrite()` verifies six longs are written in order: length, file count, directory count, quota, space consumed, space quota. `testReadFields()` stubs six reads and checks populated fields. Header and string tests compare exact fixed-width output for quota/no-quota and human-readable modes. Snapshot tests build snapshot fields and compare human-readable and raw output strings.

## State And Persistence Behavior
All state is in-memory. Serialization tests use mocked `DataInput` and `DataOutput`; no real files are written.

## Dependencies And Integration Points
`ContentSummary` output is consumed by filesystem APIs and shell commands such as count/listing output. Exact string assertions protect CLI-compatible formatting and writable field order.

## Risks
The tests are intentionally brittle with exact spacing, which is desirable for CLI compatibility but raises maintenance cost for formatting changes. They do not cover every builder field combination, negative field inputs, equality/hash behavior, or JSON/protobuf conversions.

## Test Signals
Passing confirms `ContentSummary` builder defaults, quota math display, writable compatibility, human-readable scaling, and snapshot output formatting remain stable.
