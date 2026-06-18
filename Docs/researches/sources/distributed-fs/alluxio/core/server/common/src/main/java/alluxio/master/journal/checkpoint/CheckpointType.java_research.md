# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/CheckpointType.java

## Purpose
`CheckpointType` assigns stable numeric ids to supported checkpoint encodings and their parser formats.

## Important APIs, Types, And Functions
Types include `JOURNAL_ENTRY`, `COMPOUND`, `LONGS`, `ROCKS_SINGLE`, `INODE_PROTOS`, `LONG`, and `ROCKS_PARALLEL`. Each stores an id and `CheckpointFormat`. `fromLong` maps persisted ids back to enum values with upgrade guidance on failure.

## Control Flow, State, Dependencies, Risks, And Tests
The id is persisted as a leading long by `CheckpointOutputStream`; readers use it to select parser behavior. Dependencies include concrete format classes and `RuntimeConstants`. Risks include changing ids or meanings, unknown ids from future versions failing hard, and binary formats lacking human-readable parsing. Tests should assert stable ids, `fromLong` mapping, unknown-id errors, and format instance compatibility.
