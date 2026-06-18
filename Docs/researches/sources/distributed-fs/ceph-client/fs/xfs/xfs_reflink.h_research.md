# sources/distributed-fs/ceph-client/fs/xfs/xfs_reflink.h

Purpose: Declares reflink/COW public interfaces and the safety predicate for freeing COW fork blocks.

Important APIs and functions: `xfs_can_free_cowblocks` checks dirty page, writeback, and direct-I/O state before COW fork cleanup. The header exposes sharedness trimming, COW allocation/conversion/cancel/end/recovery, remap prep/blocks/update, reflink flag scans/clears, unshare, realtime extent-size support, and max software atomic COW sizing.

Control flow and integration: Write paths call trim/allocation/conversion APIs; IO completion calls end-COW APIs; remap ioctls call prep, blocks, and update-dest; truncate/inactivation/error paths call cancel; mount recovery calls recover; maintenance paths call shared extent scans and clear flag helpers. The prototypes coordinate callers from iomap, bmap, file remap, inode cleanup, and mount recovery code.

State and persistence: The header manages no state directly. `xfs_can_free_cowblocks` reads VFS inode dirty/writeback/direct-I/O state, because persistent COW fork cleanup must not race outstanding writes that may target COW staging blocks.

Dependencies and integration points: Depends on `struct xfs_inode`, `xfs_bmbt_irec`, `xfs_trans`, VFS `struct file`, page cache tags, and atomic direct-I/O counters. It is only correct when callers hold the locking documented by the implementation.

Risks and invariants: COW cleanup requires no dirty cache, no writeback, and no direct I/O. Function declarations expose both byte-range and fsblock-range variants; callers must supply correctly converted ranges and hold expected locks. Realtime reflink constraints are centralized in `xfs_reflink_supports_rextsize`.

Test signals: Compile/link coverage from writeback, direct I/O, remap, truncate, recovery, and realtime grow paths; unit-style checks for `xfs_can_free_cowblocks` under dirty/writeback/dio states; and API misuse tests around range conversion boundaries.
