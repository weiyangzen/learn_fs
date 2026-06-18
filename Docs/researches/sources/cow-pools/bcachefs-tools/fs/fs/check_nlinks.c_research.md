# File Research: sources/cow-pools/bcachefs-tools/fs/fs/check_nlinks.c

## Purpose

Repairs hardlink counts for non-directory inodes.

## Main Interfaces

- `bch2_check_nlinks(struct bch_fs *c)`.

## Behavior

The pass builds an in-memory `nlink_table` for inodes that are non-directories and have nonzero `bi_nlink`. It then walks all dirents and increments link counts for visible dirents pointing to in-range non-directory targets, using snapshot visibility rules from `bch2_ref_visible()`. Finally it walks inode keys again and updates inode nlink fields when the stored count differs from the counted value, or when unlinked state conflicts with nonzero nlink.

To bound memory, it processes inode ranges. If table allocation fails while collecting hardlink candidates, it records the next range boundary and finishes the current range before continuing.

## State And Side Effects

Allocates a growable `kv*` table, sorts it by inode number, scans dirents, and transactionally rewrites inode nlink fields.

## Dependencies

Uses `check.h`, Linux `bsearch`, btree iteration/commit helpers, inode unpack/write helpers, and snapshot visibility tracking.

## Notes

Directories are excluded because directory nlink/subdirectory counts are handled by the dirent/directory structure checks.
