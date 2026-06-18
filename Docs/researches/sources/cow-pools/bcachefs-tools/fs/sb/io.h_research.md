# File Research: sources/cow-pools/bcachefs-tools/fs/sb/io.h

Public interface for superblock IO and optional-field manipulation. It defines the scratch read buffer size, version compatibility predicate, field access/resize macros, `field_to_type()`, and `bch_sb_field_ops`.

Exports read/write/validate functions, superblock copy functions between disk and in-memory fs/device handles, feature-setting helpers, version downgrade/upgrade entry points, and text printers for superblocks, layouts, and fields. Inline magic helpers derive bset/jset magic from the filesystem UUID.
