# File Research: sources/cow-pools/bcachefs-tools/src/commands/list_journal.rs

## Purpose
Implements `bcachefs list_journal`, a detailed journal inspection command with sequence filtering, missing-range reporting, transaction/log/key filters, blacklisted-entry handling, and optional key value printing.

## Main Interfaces
- CLI struct: `Cli`
- Command export: `CMD = typed_cmd!("list_journal", ...)`
- Key types:
  - `JournalEntries`
  - `JournalFilter`
  - `TransactionMsgFilter`
  - `TransactionKeyFilter`
- Major helpers:
  - `journal_replay_print`
  - `print_one_entry`
  - `parse_seq_range`
  - `parse_sign`
  - `entry_matches_range`
  - `should_print_transaction`

## Behavior
- Opens devices in read-only, no-recovery, no-change, degraded, continue-on-error, journal-only mode.
- Supports reading all entries, dirty-only entries, a count of recent entries, or a specific sequence/range.
- Reports missing journal ranges using `bch2_journal_entry_missing_range`.
- Can include or suppress blacklisted entries.
- Can restrict output to flush entries, datetime entries, headers only, log-containing transactions, btree IDs, transaction log patterns, or key ranges.
- Can print offsets of journal subentries and suppress bkey values.
- In unfiltered mode, prints journal headers and all matching entries.
- In filtered mode, identifies transaction boundaries and prints only matching transactions, optionally printing all headers.

## Dependencies and Coupling
- Uses journal helpers from `bch_bindgen::journal`.
- Uses `bbpos_range_parse` and bkey range matching logic.
- Uses C text renderers:
  - `bch2_journal_ptrs_to_text`
  - `bch2_prt_jset_entry_type`
  - `bch2_btree_id_level_to_text`
  - `bch2_bkey_to_text`
  - `bch2_journal_entry_to_text`
- Uses `read_flag_list` with `__bch2_btree_ids`.

## Important Implementation Notes
- Blacklisted entries are printed with leading spaces converted to `*` at line starts, preserving visual distinction.
- Log filtering excludes internal subsystem markers: rebalance, reconcile, copygc, promote.
- Key range matching intentionally collapses start to end to match the C behavior noted in the source.
- `-n` computes max sequence from collected entries because `journal.seq` is not available in read-journal-only mode.

## Risks and Edge Cases
- Transaction boundary logic depends on jset entry ordering and classification helpers.
- Filter behavior is subtle where positive and negative key ranges combine.
- `star_start_of_lines` is custom formatting logic and may not cover every leading-space case.
- Large journals can consume memory in collected C replay arrays and Rust vectors.
