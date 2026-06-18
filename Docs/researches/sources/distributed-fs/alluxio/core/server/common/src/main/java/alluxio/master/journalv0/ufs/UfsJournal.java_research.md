# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsJournal.java

## Purpose
`UfsJournal` is the legacy read-only UFS journal implementation. It defines the directory layout and exposes reader creation and formatted-state detection.

## Important APIs, Types, and Functions
Important methods are `getCompletedLocation()`, `getCheckpoint()`, `getCurrentLog()`, `getCompletedLog(long)`, `getJournalFormatter()`, `getLocation()`, `getReader()`, and `isFormatted()`. Constants define `completed/`, `log.out`, `checkpoint.data`, and zero-padded completed log filenames.

## Control Flow, State, and Persistence
The class stores a journal URI and a formatter. It maps checkpoint and log concepts to deterministic UFS paths: the current log lives in the base directory, completed logs live in `completed/log.%020d`, and the checkpoint is `checkpoint.data`. `isFormatted()` opens the UFS, lists the base path, and searches for a configured format-file prefix.

## Dependencies and Integration Points
It depends on Alluxio configuration, `UnderFileSystem`, `UnderFileSystemConfiguration`, `UfsStatus`, `URIUtils`, and `JournalFormatter`. It is used by both read-only `Journal.Factory` and mutable subclasses.

## Risks and Test Signals
Risks include unformatted directories returning `null` from `listStatus()`, path construction failures, format-prefix false positives, and timestamp/path behavior across UFS implementations. Signals include formatted and unformatted detection, reader creation, completed-log path ordering, and compatibility with `UfsJournalWriter`.
