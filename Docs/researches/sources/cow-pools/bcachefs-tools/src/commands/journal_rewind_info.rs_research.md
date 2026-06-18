# File Research: sources/cow-pools/bcachefs-tools/src/commands/journal_rewind_info.rs

## Purpose
Implements `bcachefs journal_rewind_info`, a diagnostic command that reports the safe journal rewind window and lists flush entries that can be used as rewind targets.

## Main Interfaces
- CLI struct: `Cli`
- Command export: `CMD = typed_cmd!("journal_rewind_info", ...)`
- Key helpers:
  - `JournalEntries`
  - `jset_datetime`
  - `jset_rewind_limit`
  - `entry_payload_le64`
  - `fmt_secs`

## Behavior
- Opens devices read-only with no recovery, no changes, severe degraded tolerance, continue-on-error, retained recovery info, and full journal-only reading.
- Collects C journal replay entries through `rust_collect_journal_entries`.
- Finds the latest journal entry by sequence number.
- Reads that entry’s `rewind_limit` payload to determine the oldest safe rewind sequence.
- Falls back to the lowest sequence present if the latest entry lacks a rewind-limit subentry.
- Lists flush entries in `[floor_seq, latest_seq]`, including datetimes when available.
- `-n 0` prints all candidates; positive `-n` prints the most recent N candidates.
- Prints candidate count and total entries in the rewind window.

## Dependencies and Coupling
- Shares a `JournalEntries` RAII wrapper pattern with `list_journal.rs`.
- Depends on raw jset entry layout because bindgen does not expose datetime/rewind-limit payload structs.
- Uses `jset_entries`, `entry_type`, and `jset_no_flush` from journal bindings.
- Uses `chrono::Utc` for timestamp formatting.

## Important Implementation Notes
- `entry_payload_le64` reads the first payload u64 from byte offset 8 of `jset_entry`.
- Only flush entries are considered rewind targets.
- Output is built as a string, then printed once.

## Risks and Edge Cases
- Raw payload reads assume the C `jset_entry` layout and payload endianness.
- If journal collection returns no entries, the command fails.
- If the latest entry lacks rewind-limit data, fallback is conservative but may overstate safety depending on old formats.
