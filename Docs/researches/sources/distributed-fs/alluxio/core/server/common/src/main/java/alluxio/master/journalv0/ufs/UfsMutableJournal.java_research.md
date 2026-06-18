# sources/distributed-fs/alluxio/core/server/common/src/main/java/alluxio/master/journalv0/ufs/UfsMutableJournal.java

## Purpose
`UfsMutableJournal` adds formatting and writer creation to `UfsJournal`, making a legacy UFS journal writable.

## Important APIs, Types, and Functions
It implements `format()` and `getWriter()`. Formatting uses `UnderFileSystem`, `UfsStatus`, recursive `DeleteOptions`, `URIUtils`, and `UnderFileSystemUtils.touch()`.

## Control Flow, State, and Persistence
`format()` opens the UFS, deletes every child of the journal directory if it exists, creates the directory if it does not, and writes a format breadcrumb whose name starts with the configured master format-file prefix and ends with the current timestamp. `getWriter()` returns a new `UfsJournalWriter` for this journal.

## Dependencies and Integration Points
It depends on `UfsJournal`, `MutableJournal`, Alluxio configuration, UFS APIs, and path utilities. It is used by `MutableJournal.Factory` to initialize writable legacy journals.

## Risks and Test Signals
Risks include destructive deletion of the journal directory contents, failure to delete nested directories or files, format breadcrumb prefix collisions, and repeated writer creation without external coordination. Signals are format clearing files/directories, directory creation, breadcrumb detection by `isFormatted()`, and writer persistence round trips.
