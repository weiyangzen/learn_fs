# sources/distributed-fs/ceph-client/fs/jfs/jfs_discard.c

## Purpose
Implements online discard issuing and FITRIM range handling for JFS.

## Important APIs, types, and functions
`jfs_issue_discard()` wraps `sb_issue_discard()`. `jfs_ioc_trim()` converts byte ranges to filesystem blocks, validates against the bmap, iterates AGs, and calls `dbDiscardAG()`.

## Control flow
FITRIM enters from `jfs_ioctl()`. The range is shifted to block units, `minlen` is rounded to at least one block, `s_umount` is held read-side, invalid ranges are rejected, end is clamped, and each overlapping AG is trimmed.

## State and persistence behavior
Discard informs the block device about free blocks without changing logical data. `dbDiscardAG()` may temporarily allocate free ranges and free them again.

## Dependencies and integration points
Depends on block discard support, JFS superblock/bmap state, dmap trimming, and debug logging.

## Risks and test signals
Test unsupported devices, partial/full ranges, minlen filtering, concurrent allocation/free, online discard mount option, and discard failure logging.
