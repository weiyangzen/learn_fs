# File Research: sources/cow-pools/bcachefs/fs/bcachefs/fs/dirent_format.h

Defines the on-disk bcachefs dirent value format and directory-name constants.

Key elements:
- Dirent keys store a 64-bit string hash in the key offset and resolve collisions by linear probing.
- `struct bch_dirent` stores either a target inode number or parent/child subvolume IDs for `DT_SUBVOL`.
- `d_type` stores file type bits copied from target inode mode; `d_casefold` indicates the casefolded-name layout.
- Non-casefolded entries store a flexible `d_name`.
- Casefolded entries store original length, folded length, and concatenated original/folded names in `d_cf_name_block`.
- Defines `DT_SUBVOL = 16`, `BCH_DT_MAX = 17`, and `BCH_NAME_MAX = 512`.

Important invariants:
- Linear probing requires hash whiteouts on deletion when collisions exist.
- Dirent values are packed and 8-byte aligned.
- Subvolume dirents encode two 32-bit subvolume IDs instead of an inode number.

Filesystem relevance:
- This is the persistent directory-entry ABI that lookup, rename, readdir, and fsck code interpret.
