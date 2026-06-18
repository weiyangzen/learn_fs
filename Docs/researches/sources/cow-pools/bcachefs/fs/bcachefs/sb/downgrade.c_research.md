# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/downgrade.c

This file manages superblock policy for metadata version upgrades and downgrades.

Key responsibilities:
- Defines upgrade and downgrade tables mapping metadata version crossings to required recovery passes and fsck errors that should be fixed silently.
- Handles all-fsck recovery pass expansion for broad upgrade requirements.
- Adds extra upgrade requirements for version-specific conditions such as existing stripes.
- Writes required recovery passes and silent-error bitmaps into the superblock extension field on upgrade.
- Builds the downgrade superblock field containing per-version recovery/error requirements for older tools/kernels.
- Validates and renders the downgrade field.
- Applies downgrade entries when lowering allowed/current minor versions by merging required passes and silent errors into in-memory and on-disk extension state.

Important invariants:
- Downgrade entries are packed and only 2-byte aligned; iteration carefully checks bounds before accessing flexible-array errors.
- Downgrade entries must match the major version of the current superblock.
- Entries below `version_incompat` are omitted because older compatible downgrade paths cannot safely apply past incompatible format use.
- The downgrade field is only updated once the B-tree subsystem is running, because some conditions depend on live filesystem state.
