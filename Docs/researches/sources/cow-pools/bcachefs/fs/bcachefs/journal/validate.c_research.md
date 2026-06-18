# File Research: sources/cow-pools/bcachefs/fs/bcachefs/journal/validate.c

This file validates and renders journal sets and individual journal entries. It is the journal-side metadata integrity gate used both when reading/replaying journal entries and before writing journal data.

Key responsibilities:
- Builds contextual journal error messages with version, entry type, sequence, and offset.
- Validates journal bkeys for nonzero size, bounds, key format, compatibility conversion, and type-specific bkey validity.
- Repairs some corrupt entries under fsck policy by shrinking/removing invalid keys and zeroing trailing entry space.
- Validates all supported `BCH_JSET_ENTRY_*` payload types through a dispatch table.
- Renders journal entry contents for diagnostics.
- Validates whole `jset` headers: magic, compatible metadata version, checksum type, `last_seq <= seq`, and entry bounds.
- Provides early validation before full read when only bucket-bound size checks are possible.

Important invariants:
- Entry iteration must never advance past the enclosing `jset`/clean-section vstruct end.
- On write validation failures, errors are counted and may force filesystem inconsistency handling rather than silent writeout.
- `btree_root` entries intentionally keep the entry wrapper even if contents are nulled so later recovery can tell a root was expected.
- Unknown journal entry types are tolerated by returning success if the type is outside the known dispatch table.

Dependencies include bkey validation/compatibility, fsck error handling, replicas validation, journal format helpers, superblock magic/checksum helpers, and printbuf diagnostics.
