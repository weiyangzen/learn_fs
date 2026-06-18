## sources/distributed-fs/ceph-client/fs/xfs/xfs_itable.c

Purpose: implements bulk inode stat and inode-number table export. It walks allocated inode records, formats `struct xfs_bulkstat` or `struct xfs_inumbers`, advances request cursors, and delegates userspace formatting to caller-supplied callbacks.

Important APIs and functions: public entry points are `xfs_bulkstat_one`, `xfs_bulkstat`, `xfs_bulkstat_to_bstat`, `xfs_inumbers`, and `xfs_inumbers_to_inogrp`. Internal helpers include `xfs_bulkstat_one_int`, `xfs_bulkstat_iwalk`, `xfs_bulkstat_already_done`, `xfs_inumbers_walk`, and `want_metadir_file`.

Control flow: bulkstat allocates a temporary buffer and empty transaction, then stats either one inode or walks inode btree records through `xfs_iwalk`. `xfs_bulkstat_one_int` igets each inode with untrusted/dontcache flags, reloads incomplete unlinked buckets when needed, skips freed/private/superblock inodes unless metadata-directory output was requested, fills ownership/timestamps/extent/health/block fields, calls the formatter, and advances `startino` unless a runtime error must be replayed to userspace. Inumbers walks inobt records via `xfs_inobt_walk`, formats chunk start/count/free-mask data, and advances by `XFS_INODES_PER_CHUNK`.

State and persistence: normally read-only, but it can reload incomplete unlinked-list state and force shutdown on unrecoverable in-core corruption. It reads inode core/fork state, delayed block counts, health bits, and inobt allocation records. Request state (`startino`, `ocount`, `ubuffer`) is advanced in memory.

Dependencies and integration: depends on iwalk/inobt traversal, inode cache, quota/idmap ownership translation, health reporting, and ioctl formatters. Native and compat ioctls pass formatter callbacks that copy results to userspace ABI layouts.

Risks and test signals: cursor advancement must avoid duplicates or skipped inodes across calls, private metadata leakage must be prevented, idmapped mounts are rejected, formatter `-ECANCELED` must be hidden from userspace, and stale inobt records must not crash the walk. Tests should cover single and bulk modes, buffer-full restarts, AG-limited requests, metadata directory flag behavior, nrext64 flag behavior, idmapped mount rejection, freed inode races, and inumbers chunk masks.
