<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/iscan.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/iscan.h

Purpose: Defines the live inode scan state and API used by online scrub/repair components that need full-filesystem inode iteration plus live-update filtering.

Important APIs, types, and functions: `struct xchk_iscan` stores scrub context, mutex, scan start, next cursor, optional skip inode, last visited inode, opstate bits, iget retry settings, batch base, skipped mask, and cached inode references. Defines opstate bits `XCHK_ISCAN_OPSTATE_ABORTED` and `XCHK_ISCAN_OPSTATE_TRYLOCK_AGI`, inline abort/trylock helpers, and the iterator/lifecycle prototypes.

Control flow: Callers start a scan, optionally set abort or AGI trylock mode, call `xchk_iscan_iter()` until it returns zero or error, mark each inode visited, finish any batch, and teardown. Hook code calls `xchk_iscan_want_live_update()` while holding appropriate inode locks.

State and persistence: The header defines only in-memory scan cursor state. The mutex protects fields shared with live update hooks. Inode references stored in `__inodes[]` must be released by iterator finish or teardown.

Dependencies and integration points: Exposes XFS inode and scrub types to directory, parent, inode repair, and future index-rebuild code. Its contracts rely on AGI locks and caller-held inode locks described in `iscan.c`.

Risks and test signals: Misusing private cursor fields can break live-update correctness. Test API users for balanced start/teardown, abort propagation, skip_ino filtering, trylock mode, and no leaked batched inode references on early exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/iscan.h -->
