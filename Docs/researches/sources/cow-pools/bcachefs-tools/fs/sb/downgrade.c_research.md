# File Research: sources/cow-pools/bcachefs-tools/fs/sb/downgrade.c

This file manages metadata-version upgrade/downgrade recovery requirements stored in the superblock.

Key responsibilities:
- Defines upgrade and downgrade tables mapping metadata versions to required recovery passes and fsck errors to silence.
- Applies upgrade requirements with `bch2_sb_set_upgrade()` and `bch2_sb_set_upgrade_incompat()`.
- Adds special upgrade requirements with `bch2_sb_set_upgrade_extra()`.
- Builds and updates the `BCH_SB_FIELD_downgrade` superblock field with `bch2_sb_downgrade_update()`.
- Applies downgrade requirements when moving from an older minor version range to a newer current version with `bch2_sb_set_downgrade()`.
- Validates and prints downgrade superblock entries.

Important behavior:
- `RECOVERY_PASS_ALL_FSCK` expands to the fsck recovery pass mask.
- Upgrade entries set bits in `ext->recovery_passes_required` and `ext->errors_silent`.
- Extra upgrade handling for `bucket_stripe_sectors` requires allocation checks if stripes exist.
- Downgrade field generation skips entries from other major versions or entries older than the incompatible version floor.
- Downgrade entries are variable length with packed 2-byte alignment.
- Applying downgrade entries ORs recovery pass bits and marks listed errors silent in both in-memory and superblock ext state.

Important invariants:
- Downgrade validation requires entry major version to match the superblock major version.
- On write validation, entries may not overrun the superblock field.
- Empty 2-byte-aligned tail entries at the end are tolerated.
- Downgrade field resize does not shrink an existing larger field.

Dependencies:
- Uses metadata version constants, recovery pass stable conversion, fsck error IDs, superblock ext fields, btree stripe-root state, darrays, and errors text formatting.

Research notes:
- This file is compatibility policy. It encodes which repair/scanning passes are needed when metadata semantics change across versions.
