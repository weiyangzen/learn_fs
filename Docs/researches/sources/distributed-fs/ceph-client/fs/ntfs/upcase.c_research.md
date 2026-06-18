# sources/distributed-fs/ceph-client/fs/ntfs/upcase.c

## Purpose
Generates the default NTFS Unicode upcase table used for case-insensitive comparisons when a volume-specific `$UpCase` table is unavailable or matches the default.

## Important APIs, Types, And Functions
`generate_default_upcase()` allocates `default_upcase_len` little-endian `__le16` entries, initializes each entry to identity, then applies three compressed mapping tables: range deltas, alternating duplicate ranges, and individual word replacements.

## Control Flow
The generator is called from `ntfs_fill_super()` under `ntfs_lock` when the global default table is absent. Mount later compares the volume `$UpCase` table with this default in `load_and_init_upcase()` and may share the global table through `ntfs_nr_upcase_users`.

## State And Persistence
This file allocates in-memory data only. The table is freed by volume teardown when the global reference count drops to zero. It does not write `$UpCase`; it only supplies a fallback/comparison table.

## Dependencies And Integration Points
Depends on endian helpers and `default_upcase_len` from NTFS headers. Used by Unicode comparison/collation in `unistr.c` and by directory/index lookup.

## Risks And Edge Cases
Allocation failure prevents creation of the default table; mount can still use the volume table if available. Correctness depends on the static mapping tables matching NTFS expectations; bad mappings can cause lookup/collation mismatches versus Windows.

## Test Signals
Verify selected ASCII, Greek, Cyrillic, fullwidth, and explicit word mappings; ensure identity for unmapped code points; test allocation failure with a valid volume `$UpCase`; and compare case-insensitive lookup behavior with a known NTFS image.
