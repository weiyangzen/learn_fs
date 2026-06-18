# sources/distributed-fs/ceph-client/fs/xfs/libxfs/xfs_attr_remote.h

## Purpose
`xfs_attr_remote.h` declares the remote extended-attribute value API. It exposes sizing helpers and the read/write/allocation/removal functions used by the attr core and leaf state machine when values are stored out of line in attr-fork extents.

## Important APIs, types, and functions
The header declares `xfs_attr3_rmt_blocks` and inline `xfs_attr3_max_rmt_blocks`, plus remote value functions `xfs_attr_rmtval_get`, `xfs_attr_rmtval_stale`, `xfs_attr_rmtval_invalidate`, `xfs_attr_rmtval_remove`, `xfs_attr_rmt_find_hole`, `xfs_attr_rmtval_set_value`, `xfs_attr_rmtval_set_blk`, and `xfs_attr_rmtval_find_space`.

## Control flow
The exported functions are used in two phases. Set/replace operations first find a hole and allocate blocks through intent-based helpers, then synchronously write the value and publish the leaf entry. Get operations use `xfs_attr_rmtval_get` after leaf lookup fills remote block metadata. Remove and replace cleanup invalidate stale buffers and unmap extents through the intent retry loop.

## State and persistence behavior
The header defines the remote-block count contract: max remote blocks are computed from `XFS_XATTR_SIZE_MAX`, not a fixed byte-to-fsb conversion, because CRC remote value headers consume payload space. Callers are expected to keep `struct xfs_da_args` and `struct xfs_attr_intent` remote fields synchronized while progressing through transactions.

## Dependencies and integration points
It depends on `struct xfs_mount`, `struct xfs_da_args`, `struct xfs_inode`, `struct xfs_bmbt_irec`, and `struct xfs_attr_intent` definitions from including translation units. It is consumed by `xfs_attr.c` and `xfs_attr_leaf.c` and implemented by `xfs_attr_remote.c`.

## Risks and edge cases
Callers must distinguish `xfs_attr_rmtval_set_blk`, which allocates extents under the active transaction, from `xfs_attr_rmtval_set_value`, which writes already allocated remote buffers synchronously. Removing remote values can require repeated calls. The max-block helper must be used for reservations that do not yet know the exact removed value length.

## Test signals
Compilation should catch prototype drift. Runtime tests should cover remote get/set/remove through public xattr operations and verify that reservation code using `xfs_attr3_max_rmt_blocks` handles worst-case CRC header overhead.
