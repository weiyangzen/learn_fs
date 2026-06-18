# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointFormat.java

## Purpose
`CheckpointFormat` defines the parsing and human-readable rendering contract for checkpoint binary formats.

## Important APIs, Types, And Functions
Implementations provide `createReader(CheckpointInputStream)` and `parseToHumanReadable`. The nested marker interface `CheckpointReader` identifies non-thread-safe reader types.

## Control Flow, State, Dependencies, Risks, And Tests
`CheckpointType` maps type ids to concrete format implementations. This interface has no state or persistence by itself, but defines how persisted checkpoint bytes are interpreted. Dependencies are `CheckpointInputStream`, `PrintStream`, and IO exceptions. Risks include format readers not validating input type, unavailable human-readable rendering for binary formats, and reader lifetime tied to input stream ownership. Tests should verify every `CheckpointType` format creates the correct reader and handles parse output/failures.
