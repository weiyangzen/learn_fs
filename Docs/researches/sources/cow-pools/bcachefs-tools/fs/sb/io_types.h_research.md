# File Research: sources/cow-pools/bcachefs-tools/fs/sb/io_types.h

Defines `struct bch_sb_cpu`, the endian-converted in-memory summary populated by `bch2_sb_update()`. It mirrors stable superblock identity, version fields, device count, clean/encryption state, feature/compat bits, extent encoding metadata, time conversion values, required recovery passes, silenced fsck errors, and btrees with lost data.

This structure is the runtime cache used outside direct superblock parsing paths.
