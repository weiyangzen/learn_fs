# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_dir2.h

## Purpose
`xfs_dir2.h` is the public/private interface for XFS directory version 2/3 operations. It declares directory APIs, buffer verifier symbols, conversion helpers for directory logical address spaces, name validation and ascii-ci helpers, optional live hook interfaces, and parent-pointer-aware child update structures.

## Important APIs, Types, And Functions
The header declares `xfs_name_dot` and `xfs_name_dotdot`, `xfs_dir2_samename()`, `enum xfs_dir2_fmt`, mount lifecycle functions, generic directory mutation/lookups, direct `xfs_da_args` variants, block/data helper APIs, inode-number validation, and buffer ops for block, leaf, free, and data blocks.

Inline conversion helpers translate between directory byte offsets, dataptrs, logical directory blocks (`xfs_dir2_db_t`), DA blocks, and block offsets. `xfs_dir2_block_tail_p()` and `xfs_dir2_leaf_tail_p()` locate tail records based on mount geometry. The ascii-ci helpers transform only supported ASCII/Latin uppercase bytes. `struct xfs_dir_update` carries parent/name/child/parent-pointer args for create/add/remove/rename/exchange helpers.

## Control Flow
Most flow is declarative through prototypes and inline arithmetic. Callers use the conversion helpers heavily when converting leaf addresses to data-entry pointers, logging tail areas, mapping directory spaces, and formatting readdir offsets. When `CONFIG_XFS_LIVE_HOOKS` is disabled, hook calls compile to no-ops; otherwise hook registration and update callbacks are provided by `xfs_dir2.c`.

## State And Persistence
The header itself stores no state, but its conversions define the persistent directory address ABI: data, leaf, and free spaces are separated by large fixed offsets and converted through geometry. `struct xfs_dir_update` drives persistent dirent and parent-pointer updates. The declared buffer ops enforce persistent block format checks for block/data/leaf/free metadata.

## Dependencies And Integration Points
It includes DA format and btree headers and is used by all directory implementation files plus bmap and higher-level inode operations. It integrates with parent pointer code, online fsck hooks, buffer verifiers, and VFS-facing directory functions.

## Risks
Arithmetic helper regressions can corrupt every directory format because dataptrs and DA blocks are stored on disk. The ascii-ci transform is intentionally narrow; treating it as general Unicode casefolding would be incorrect. Hook configuration must avoid lock inversions because enabling/disabling static branches can take CPU hotplug locks. The child update API assumes callers already hold required inode locks.

## Test Signals
Tests should verify offset conversions round-trip for multiple directory block sizes, block/leaf tail pointer placement, name validation around `MAXNAMELEN`, filetype conversion paths, hook stubs in disabled builds, live hook notifications in enabled builds, and parent-pointer child update APIs across create/add/remove/rename/exchange.
