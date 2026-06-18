# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/downgrade.h

This header declares the downgrade/upgrade policy interface.

Public functions:
- Update the downgrade superblock field.
- Record compatible and incompatible upgrade requirements.
- Apply extra upgrade requirements.
- Apply downgrade requirements for a minor-version transition.

It exports `bch_sb_field_ops_downgrade` for generic superblock field validation/rendering.
