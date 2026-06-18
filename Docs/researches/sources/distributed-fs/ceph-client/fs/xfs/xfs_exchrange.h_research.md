# sources/distributed-fs/ceph-client/fs/xfs/xfs_exchrange.h

## Purpose
`xfs_exchrange.h` declares the internal representation and entry points for XFS file range exchange and commit-range support.

## Important APIs, types, and functions
The header defines private flag bits `__XFS_EXCHANGE_RANGE_UPD_CMTIME1`, `__XFS_EXCHANGE_RANGE_UPD_CMTIME2`, and `__XFS_EXCHANGE_RANGE_CHECK_FRESH2`, grouped in `XFS_EXCHANGE_RANGE_PRIV_FLAGS`. `struct xfs_exchrange` stores both `struct file` pointers, byte offsets, length, user-visible flags, and file2 freshness fields. It declares the three ioctl handlers, the inode lock/unlock helpers used by exchange-map code, and `xfs_exchrange_estimate`.

## Control flow
Callers build `struct xfs_exchrange` from ioctl arguments or scrub repair state and pass it to the implementation in `xfs_exchrange.c`. The private flags are set internally after VFS checks or commit-range freshness setup; they must not overlap public `XFS_EXCHANGE_RANGE_*` flags.

## State and persistence
The header owns no storage. Its private flags control transaction-time timestamp updates and freshness validation, which affect on-disk inode metadata only when the implementation commits an exchange.

## Dependencies and integration points
It depends on XFS transaction and inode types through forward declarations and is included by exchange-range implementation, exchange-map intent recovery, and scrub temporary-file repair code.

## Risks and test signals
The key risk is flag-space collision with user ABI flags, guarded by build-time checks in the implementation. Test signals are compile coverage of ioctl handlers, scrub repair exchange-map paths, and any future flag additions.
