# sources/distributed-fs/ceph-client/fs/xfs/scrub/repair.h

## Purpose
`repair.h` is the internal interface for XFS online repair. It declares shared repair helpers, setup functions, repair entry points, revalidators, and no-repair stubs so scrub code can compile uniformly with or without `CONFIG_XFS_ONLINE_REPAIR`.

## Important APIs, types, and functions
The header defines `xrep_notsupported`, `xrep_trans_commit`, and `struct xrep_find_ag_btree`. It declares the generic repair control helpers, AG/rtgroup setup helpers, quota helpers, xfile setup, metadata inode helpers, per-AG and realtime repair entry points, and reinitialization helpers. Under realtime and quota Kconfig blocks it either exposes real functions or maps them to `xrep_notsupported`/no-op stubs.

## Control flow
Consumers include `repair.h` and call setup/repair routines through scrub operation tables. In online-repair builds, declarations bind to concrete implementations across scrub repair files. In no-repair builds, `xrep_will_attempt` still returns true for force rebuild or corruption so `xrep_attempt` can report `-EOPNOTSUPP`; setup functions become no-ops to avoid blocking scrub-only operation.

## State and persistence
The header stores no state, but it defines the contracts for stateful repair: transaction ownership, perag/rtgroup cursors, temporary xfile buffers, quota flag updates, inode block counters, reservation resets, and staged btree roots.

## Dependencies and integration points
It depends on scrub core declarations, quota type definitions, AG reservation types, btree buffer ops, and realtime Kconfig. It is the integration point between generic scrub setup files and specialized repair modules such as rmap, refcount, rtbitmap, rtsummary, rtrmap, and rtrefcount repair.

## Risks and test signals
Risks are signature drift between declarations and implementations, incorrect stubs hiding unsupported repairs, Kconfig mismatches for realtime/quota entry points, and callers assuming setup side effects in no-repair builds. Test signals include compile coverage for repair enabled/disabled, realtime enabled/disabled, quota enabled/disabled, force rebuild on no-repair kernels, and operation tables resolving every declared repair entry correctly.
