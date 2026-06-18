# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journal/JournalReader.java

## Purpose
`JournalReader` defines sequential reading over checkpoint and log elements in a journal.

## Important APIs, Types, And Functions
It declares `advance`, `getEntry`, `getCheckpoint`, `getNextSequenceNumber`, and `close`. `State` distinguishes `CHECKPOINT`, `LOG`, and `DONE`.

## Control Flow, State, Dependencies, Risks, And Tests
Consumers call `advance`, then read either the current checkpoint stream or log entry; repeated getters return the same current item until the next advance. Persistence is the journal backend's checkpoint and log data. Dependencies are `CheckpointInputStream`, `JournalEntry`, and closeable resources. Risks include misuse of getters before or after the right state, checkpoint stream ownership, and next sequence semantics after close. Tests should cover state transitions, repeated getters, sequence tracking, checkpoint/log ordering, and close behavior in concrete readers.
