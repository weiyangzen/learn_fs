<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters.h

Purpose: Defines the shared in-memory state used by filesystem summary counter scrub and repair.

Important APIs, types, and functions: `struct xchk_fscounters` records the scrub context, computed `icount`, `ifree`, `fdblocks`, `frextents`, delayed realtime extent reservations, valid inode-count bounds, and whether scrub froze the filesystem.

Control flow: `xchk_setup_fscounters()` allocates and initializes this structure; `xchk_fscounters()` fills the computed fields; `xrep_fscounters()` consumes them to reset global counters. The `frozen` bit controls strictness and cleanup.

State and persistence: The structure is transient `sc->buf` state. It mirrors values that may later be written to in-core counters and, for non-rtgroup realtime free extents, superblock state by repair.

Dependencies and integration points: Included by both scrub and repair implementations. It couples the checker and repairer, so field semantics must remain consistent across both files.

Risks and test signals: Stale or incomplete values can cause bad repairs if the incomplete flag is missed. Test setup failure cleanup, frozen and unfrozen paths, realtime delayed-reservation subtraction, and repair refusing to run when `frozen` is false.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/fscounters.h -->
