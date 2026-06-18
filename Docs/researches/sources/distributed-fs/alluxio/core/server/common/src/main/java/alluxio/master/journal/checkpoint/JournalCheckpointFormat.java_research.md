# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/checkpoint/JournalCheckpointFormat.java

## Purpose
`JournalCheckpointFormat` reads and renders checkpoints made of delimited master `JournalEntry` protobufs.

## Important APIs, Types, And Functions
`createReader` returns a `JournalCheckpointReader` that validates type `JOURNAL_ENTRY`. `nextEntry` delegates to `JournalEntryStreamReader`. `parseToHumanReadable` prints separators and protobuf text for each entry.

## Control Flow, State, Dependencies, Risks, And Tests
The persisted format is a checkpoint type header followed by repeated delimited journal entries. Dependencies include `JournalEntryStreamReader`, generated journal protobufs, and Guava preconditions. Risks include `JournalEntryStreamReader` treating truncated final payload as EOF, wrong type rejection, and large human-readable output. Tests should cover round trips, empty checkpoints, wrong type, truncated entries, and parse output.
