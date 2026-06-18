# sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_immed.c

## Purpose

`sources/distributed-fs/ceph-client/fs/freevxfs/vxfs_immed.c` implements address-space operations for VxFS immediate-data files, where file contents are stored directly inside the inode. The complete 53-line file was read for this report.

## Important APIs, Types, and Functions

The external object is `const struct address_space_operations vxfs_immed_aops`. Its only operation is `vxfs_immed_read_folio()`.

## Control Flow

When the pagecache requests a folio for an immediate inode, `vxfs_immed_read_folio()` computes a source pointer into `VXFS_INO(host)->vii_immed.vi_immed` at `folio_pos(folio)`, copies one page per folio page with `memcpy_to_page()`, marks the folio uptodate, and unlocks it.

## State and Persistence Behavior

The persisted data was already copied from the on-disk inode into `vxfs_inode_info` during inode load. Reads copy from that in-core immediate buffer into pagecache; no write path exists because the driver is read-only.

## Dependencies and Integration Points

`vxfs_inode.c` selects `vxfs_immed_aops` for immediate regular files/directories and sets inline symlink data directly for immediate symlinks. The code depends on folio/pagecache APIs and the FreeVxFS inode layout.

## Risks and Edge Cases

Immediate data capacity is small (`VXFS_NIMMED` is 96 bytes), but the read helper copies `PAGE_SIZE` chunks per folio page from the inline buffer without local length clamping. Correctness depends on pagecache read sizes and inode size limiting access; malformed sizes can be risky.

## Test Signals

Tests should include immediate symlinks, small immediate regular files, immediate directories if present, short reads at EOF, and fuzzed inode sizes under KASAN.
