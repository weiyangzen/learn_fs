# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/journal/tool/UfsJournalDumper.java

## Purpose
`UfsJournalDumper` implements journal dumping for legacy UFS-backed journals. It reads checkpoints and edit logs with `UfsJournalReader` and writes human-readable checkpoint files plus `edits.txt`.

## Important APIs, types, and functions
The constructor delegates common setup to `AbstractJournalDumper`. `dumpJournal()` creates a `UfsJournalSystem` at the input URI, creates a journal for a `NoopMaster` named by `mMaster`, opens `UfsJournalReader` at `mStart`, and loops until done or `mEnd`. `getJournalLocation(String)` ensures a trailing slash and parses a URI.

## Control flow
The reader state machine emits `CHECKPOINT`, `LOG`, or `DONE`. Checkpoints are read through `readCheckpoint` into `checkpoints-${nextSequenceNumber}`. Log entries are printed to `edits.txt` preceded by an 80-character separator. Unknown reader states throw.

## State and persistence behavior
The dumper is read-only against the journal and writes output files under the dump directory. It uses try-with-resources for journal, output stream, and reader cleanup.

## Dependencies and integration points
It depends on `UfsJournalSystem`, `UfsJournal`, `UfsJournalReader`, `NoopMaster`, checkpoint streams, journal protos, and URI/path handling. It is selected by `JournalTool` when `MASTER_JOURNAL_TYPE` is `UFS`.

## Risks
Input URI parsing wraps syntax errors in `RuntimeException`. The dumper prints all log entries from the selected master journal reader rather than doing additional master association filtering. Very large journals produce large single `edits.txt` files.

## Test signals
Tests should cover URI normalization, checkpoint and log state handling, end-sequence stopping, unknown state failure, missing/corrupt UFS journal behavior, and output separator formatting.
