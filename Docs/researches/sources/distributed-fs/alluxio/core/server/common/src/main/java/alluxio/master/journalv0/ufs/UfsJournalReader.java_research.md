# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsJournalReader.java

## Purpose
`UfsJournalReader` implements checkpoint-first, completed-log replay for legacy UFS journals.

## Important APIs, Types, and Functions
It implements `isValid()`, `getCheckpointInputStream()`, `getNextInputStream()`, and `getCheckpointLastModifiedTimeMs()`. State includes the journal, UFS handle, checkpoint URI, `mCheckpointRead`, checkpoint opened/last-modified times, and current completed-log number.

## Control Flow, State, and Persistence
`getCheckpointInputStream()` can be called only once, captures the checkpoint's last modified time, opens the checkpoint through UFS, wraps it with the journal formatter, and marks the checkpoint as read. `getNextInputStream()` requires the checkpoint to have been read and rejects use if the checkpoint timestamp has changed. It opens the next numbered completed log if present, increments the log number, and returns `null` when the expected log is absent.

## Dependencies and Integration Points
It depends on `UfsJournal`, `UnderFileSystem`, configuration defaults, `JournalFormatter`, and `JournalInputStream`. Replay code uses it to reconstruct state from `checkpoint.data` plus numbered completed logs.

## Risks and Test Signals
Risks include no explicit close for the reader-owned UFS handle, timestamp granularity invalidation gaps, and inability to read current `log.out` until it is completed. Signals include checkpoint-once enforcement, log numbering order, missing-checkpoint failures, checkpoint-update invalidation, and deserializer behavior on truncated logs.
