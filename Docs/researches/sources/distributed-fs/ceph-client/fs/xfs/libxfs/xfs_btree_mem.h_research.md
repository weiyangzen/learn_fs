# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_btree_mem.h

## Purpose
This header defines the lightweight state and API for xmbuf-backed in-memory btrees.  It gives the generic btree code a block-number type, daddr conversion helpers, an `xfbtree` root/geometry structure, and operation prototypes used when `CONFIG_XFS_BTREE_IN_MEM` is enabled.

## Important APIs And Types
`xfbno_t` is a 64-bit memory-btree block number.  `XFBNO_BLOCKSIZE`, `XFBNO_BBSHIFT`, and `XFBNO_BBSIZE` map xmbuf block sizing into 512-byte sector units.  `xfbno_to_daddr` and `xfs_daddr_to_xfbno` convert between memory btree block numbers and buffer daddrs.  `struct xfbtree` stores the buftarg, highest assigned block number, owner, root pointer, tree height, and min/max record arrays.

## Control Flow And State
The header-level state model is intentionally small: root pointer and height mimic on-disk btree roots, while the target and block counter provide storage allocation.  `xfbtree_verify_bno` delegates to `xmbuf_verify_daddr`; when in-memory btrees are disabled, it compiles to false to prevent accidental use.

## Dependencies, Risks, And Test Signals
The header depends on xmbuf constants and generic XFS btree declarations.  Its main risk is unit mismatch between xfbno, daddr, filesystem block, and basic-block units.  Tests should assert round-trip conversion and block-size assumptions, and config-gated builds should verify both enabled and disabled paths.
