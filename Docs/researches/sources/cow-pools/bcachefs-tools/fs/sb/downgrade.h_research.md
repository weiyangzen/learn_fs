# File Research: sources/cow-pools/bcachefs-tools/fs/sb/downgrade.h

This header declares downgrade/upgrade superblock compatibility APIs.

Key responsibilities:
- Exposes `bch_sb_field_ops_downgrade`.
- Declares:
  - `bch2_sb_downgrade_update()`
  - `bch2_sb_set_upgrade()`
  - `bch2_sb_set_upgrade_incompat()`
  - `bch2_sb_set_upgrade_extra()`
  - `bch2_sb_set_downgrade()`

Research notes:
- This is the public interface used by superblock upgrade and recovery initialization paths.
