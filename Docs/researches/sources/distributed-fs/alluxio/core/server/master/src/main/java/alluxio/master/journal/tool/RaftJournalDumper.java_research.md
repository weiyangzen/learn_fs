# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/tool/RaftJournalDumper.java

## Purpose
`RaftJournalDumper` implements offline dumping for embedded/Raft journals. It reads the local Ratis snapshot and log files directly without contacting a running quorum.

## Important APIs, types, and functions
`dumpJournal()` validates the input directory and calls `readFromDir()`. `readRatisSnapshotFromDir()` finds the latest snapshot and converts snapshot files through `readCheckpoint`. `readRatisLogFromDir()` opens Ratis storage, scans log segment paths, parses state-machine log data into `JournalEntry`, and writes selected entries. `writeSelected(PrintStream, JournalEntry)` handles aggregate and empty entries. `isSelected` filters by sequence number and master association.

## Control flow
The dumper recovers Raft storage from the journal dir, reads snapshot first, then log segments. For log entries, it ignores non-state-machine entries, parses journal entries, recursively expands aggregated journal entries, drops empty snapshotting entries, checks single-operation invariants, and writes entries whose sequence number is within `[mStart, mEnd)` and whose associated master matches `mMaster`.

## State and persistence behavior
It reads persisted Ratis snapshots and logs and writes `edits.txt` plus checkpoint directories under the output path. Snapshot MD5 is verified after reading. It does not append to or mutate Raft logs.

## Dependencies and integration points
It depends on Apache Ratis storage/log APIs, Alluxio Raft journal utilities, `SnapshotDirStateMachineStorage`, `OptimizedCheckpointInputStream`, journal proto parsing, `JournalEntryAssociation`, and `AbstractJournalDumper`.

## Risks
Direct offline reading may produce stale or partial state if used while a cluster is active. `readRatisLogFromDir` logs and swallows exceptions, so dump output can be incomplete without failing the command. Master association failures are silently filtered. Snapshot directory naming includes last-modified time, so repeated dumps can create different output paths.

## Test signals
Tests should cover missing input dir, snapshot-only and log-only journals, aggregate entries, empty entries, sequence filtering, master filtering, MD5 verification failures, corrupt log segment handling, and exception visibility.
