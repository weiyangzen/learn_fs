# sources/distributed-fs/ceph-client/fs/afs/volume.c

Purpose: Owns AFS volume records: lookup from VLDB, insertion into the cell volume tree, reference lifetime, fscache activation, server-list refresh, and volume status freshness checks.

Important APIs and functions: `afs_create_volume()` resolves a mount volume name, applies RW/RO/backup selection rules, and returns a live `struct afs_volume`. `afs_get_volume()`, `afs_try_get_volume()`, and `afs_put_volume()` manage refcounts and deferred destruction. `afs_activate_volume()` and `afs_deactivate_volume()` manage optional fscache volume cookies. `afs_check_volume_status()` ensures server lists and volume metadata are current before operations.

Control flow: `afs_create_volume()` calls `afs_vl_lookup_vldb()`, decides the desired volume type from force flags and VLDB availability, and delegates to `afs_lookup_volume()`. Allocation initializes locks, callbacks, mmap tracking, server list, volume IDs, and timestamps. Insertion uses the cell red-black tree under a seqlock and either attaches the new volume to servers or drops it in favor of an existing refcountable record.

State and persistence: A volume stores VID, all type VIDs, name, cell reference, type, server list, update deadline, creation/update volsync timestamps, cache cookie, flags, and per-volume locks. Server-list refresh can replace the RCU pointer, bump `servers_seq`, reattach to servers, and shorten the next refresh interval during RO replication.

Dependencies and integration points: Depends on VL RPC lookup, server-list allocation/annotation, cell tree/proc visibility, AFS operation keys, fscache, RCU, workqueues, and callback status logic used by vnode operations.

Risks: Volume replacement and destruction combine seqlocks, RCU, server attachment, and workqueue teardown. Refresh waiters can return `-ESTALE` after repeated update races. Name updates note a TODO for RCU-safe strings. Cache key collisions are logged and disable caching for that volume.

Test signals: Duplicate concurrent volume lookups, forced type selection failure, VLDB rename/server migration, RO replication refresh interval, fscache acquire `-EBUSY`, and interrupted waits in `afs_check_volume_status()`.
