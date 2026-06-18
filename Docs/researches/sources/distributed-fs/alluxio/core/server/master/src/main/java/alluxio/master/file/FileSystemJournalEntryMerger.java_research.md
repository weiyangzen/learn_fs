# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemJournalEntryMerger.java

## Purpose
`FileSystemJournalEntryMerger` compacts file-system master journal entries during metadata sync and inode creation flows. Its main job is to merge an inode creation entry with later inode update entries for the same inode so journal replay has fewer redundant records while preserving non-mergeable updates.

## Important APIs, types, and functions
The class implements `JournalEntryMerger`. `add(JournalEntry)` accepts raw journal entries and performs on-the-fly compaction. `getMergedJournalEntries()` exposes an unmodifiable view of the merged list. `clear()` resets the in-memory merge state. `getInodeId()` extracts ids from supported inode create/update entry variants. It uses `MutableInodeFile` and `MutableInodeDirectory` to replay update fields onto a mutable inode representation before replacing the earlier entry.

## Control flow
Create entries for files and directories are appended and indexed by inode id. Later `UpdateInode`, `UpdateInodeFile`, and `UpdateInodeDirectory` entries are appended only when no earlier create entry exists. If an earlier create entry exists, the code reconstructs a mutable inode from the create entry, applies the update, and replaces the create entry in place. Directory `UpdateInode` entries with non-empty UFS fingerprints are both merged and appended because the generic directory update path cannot fully preserve directory fingerprint behavior.

## State and persistence behavior
State is purely in memory: `mJournalEntries` holds the current compacted sequence and `mEntriesMap` maps inode id to the sequence index. The persisted effect appears when the enclosing journal context flushes the merged entries. The class is annotated `@ThreadSafe` and all public mutation/access methods are synchronized, though the class comment still says it should not be shared across threads.

## Dependencies and integration points
It depends on Alluxio journal proto entries, inode mutable models, and the `JournalEntryMerger` abstraction. `InodeSyncStream` uses it through `MetadataSyncMergeJournalContext`, and journal tests reference it together with `FileSystemMergeJournalContext`.

## Risks
The supported entry set is narrow; unsupported entries sent to `getInodeId()` throw a runtime exception. Ordering matters because replacing an early create entry with a later-mutated create entry assumes no intervening journal entry requires the old metadata. The conflicting thread-safety documentation can mislead maintainers. Directory fingerprint handling is deliberately special-cased and easy to regress when journal proto fields change.

## Test signals
Signals are in journal-context merge tests and metadata-sync flush journal tests. Useful coverage should assert create-plus-update compaction, unmerged updates without prior create entries, directory fingerprint preservation, and replay equivalence of merged versus unmerged sequences.
