# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/inode.h

Declares inode bkey operations, the unpacked inode representation, inode lookup/write/create/delete APIs, link-count helpers, inode option helpers, and subvolume inode constants.

Key elements:
- `bch2_bkey_ops_inode`, v2, and v3 wire validation, text formatting, trigger, and minimum value size.
- `bkey_is_inode()` identifies all inode key versions.
- `bch2_bkey_ops_inode_generation` and `bch2_bkey_ops_inode_alloc_cursor` define support key types.
- `struct bch_inode_unpacked` is the in-memory normalized inode representation used by VFS, fsck, and metadata code.
- `struct bkey_inode_buf` provides enough storage to pack a v3 inode plus all variable fields.
- Declares pack/unpack, v3 conversion, text formatting, lookup, oldest-snapshot lookup, write, fsck write, initialization, creation, deletion, nlink, option, casefold, and dead-inode cleanup helpers.
- Inline helpers handle inode option biasing, mode-to-type conversion, `DT_SUBVOL` reporting, flags extraction, casefold inheritance, backpointer presence, and nlink bias.
- Defines `BCACHEFS_ROOT_SUBVOL_INUM` and `subvol_inum_eq()`.

Important invariants:
- Inode options are stored with a +1 bias: zero means inherit filesystem/default option.
- Directory nlink has a different bias than non-directories.
- `bch2_inode_casefold()` falls back to filesystem option when inode option is unset.
- `bch2_inode_has_backpointer()` treats either `bi_dir` or `bi_dir_offset` as a backpointer.

Filesystem relevance:
- This is the main shared inode API surface for bcachefs metadata, VFS, fsck, dirent, ACL, and data-reconciliation code.
