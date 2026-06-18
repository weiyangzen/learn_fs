# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/clean.h

This header exposes clean-superblock section APIs.

Public functions:
- Late validation of clean-section contents.
- Verification of clean-section roots against journal roots.
- Reading the clean section from an open filesystem.
- Adding common journal/superblock entries.
- Marking filesystem state dirty or clean.

It also exports `bch_sb_field_ops_clean` for the generic superblock field dispatcher.
