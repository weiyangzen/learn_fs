# File Research: sources/cow-pools/bcachefs-tools/fs/journal/validate.c

This file validates and formats journal sets and journal entries.

Key responsibilities:
- Builds contextual journal validation error messages with `bch2_journal_entry_err_msg()`.
- Repairs invalid entry/key ranges by zeroing or compacting entries when fsck policy allows.
- Validates btree key entries, btree root entries, blacklist entries, usage entries, clock entries, device usage entries, log entries, overwrite/log-bkey/write-buffer key entries, datetime entries, and rewind entries.
- Provides per-entry text formatting through `bch2_journal_entry_to_text()`.
- Validates full `jset` structures with `bch2_jset_validate()`.
- Performs early validation during journal scan with `bch2_jset_validate_early()`.

Important validation behavior:
- Key validation rejects zero `k->u64s`, key overrun, non-current key format, and bkey validator errors.
- Read validation applies compatibility conversion before validation; write validation converts after validation.
- Invalid btree key entries can shrink or delete the bad key payload while preserving the surrounding journal structure.
- Btree root validation treats bad root sizing specially by clearing the entry contents but keeping the root entry marker.
- Blacklist v1/v2 entries enforce exact expected sizes and valid range order.
- Usage/data-usage entries enforce minimum sizes and validate replica descriptors.
- Clock entries require exact size and `rw <= 1`.
- Device usage entries require minimum size and zero padding.
- `bch2_jset_validate()` checks magic, metadata version compatibility, checksum type validity, and `last_seq <= seq` for flush entries.
- Early validation checks magic/version and truncates entries that overrun the remaining bucket sectors.

Important invariants:
- `JOURNAL_ENTRY_NONE` means no matching journal magic.
- `JOURNAL_ENTRY_BAD` means structurally present but invalid/corrupt.
- `jset->last_seq` is ignored for noflush entries.
- Entry traversal stops or truncates when `vstruct_next(entry)` exceeds the jset end.
- Validation error handling differs for read versus write through the macro in `validate.h`.

Dependencies:
- Uses bkey compatibility/validation, fsck error infrastructure, replica validation, journal format enums, and printbuf formatting.

Research notes:
- This is both a validator and a controlled repair layer for journal metadata.
- The dispatch table is generated from `BCH_JSET_ENTRY_TYPES()`, so adding a journal entry type requires matching validate/to_text functions.
