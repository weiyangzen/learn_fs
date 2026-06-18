# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/sysctl_os.c

## Scope

FreeBSD sysctl namespace and tunable setter glue for OpenZFS. It creates `vfs.zfs.*` subtrees and implements validation/update callbacks for ARC, L2ARC, metaslab, MMP, deadman, RAIDZ, SPA, vdev, spacemap, and ZIO tunables.

## Main Interfaces

- Sysctl nodes: `arc`, `brt`, `condense`, `dbuf`, `dbuf_cache`, `deadman`, `dedup`, `l2arc`, `livelist`, `lua`, `metaslab`, `mg`, `multihost`, `prefetch`, `reconstruct`, `recv`, `send`, `spa`, `trim`, `txg`, `vdev`, `vnops`, `zevent`, `zil`, and `zio`.
- ARC setters: `param_set_arc_u64()`, `param_set_arc_int()`, `param_set_arc_max()`, `param_set_arc_min()`, `param_set_arc_free_target()`, `param_set_arc_no_grow_shift()`.
- L2ARC setter: `param_set_l2arc_dwpd_limit()`.
- Other setters: `param_set_active_allocator()`, `param_set_multihost_interval()`, `param_set_deadman_synctime()`, `param_set_deadman_ziotime()`, `param_set_deadman_failmode()`, `param_set_raidz_impl()`, `param_set_slop_shift()`, `param_set_min_auto_ashift()`, `param_set_max_auto_ashift()`.

## State And Control Flow

Most setters call `sysctl_handle_*`, return unchanged on read/no new value, validate ranges, mutate the global tunable, and trigger the relevant side effect. ARC setters call `arc_tuning_update()`. DWPD changes reset L2ARC endurance counters. Multihost interval changes signal MMP threads when SPA is initialized. Deadman setters propagate timing to SPA deadman state. RAIDZ implementation selection allocates a temporary string buffer and delegates validation to `vdev_raidz_impl_set()`.

## Dependencies

Depends on FreeBSD sysctl handlers, ARC/L2ARC globals, vdev ashift globals, MMP/deadman/metaslab common setters, and OpenZFS version metadata.

## Correctness Notes

`param_set_arc_max()` and `param_set_arc_min()` validate against minimum ARC size, current opposite bound, and total memory. `debugflags` intentionally prevents enabling `ZFS_DEBUG_MODIFY` after boot because ARC buffers would lack debug checksum metadata. `param_set_deadman_ziotime()` assigns `zfs_deadman_ziotime_ms` but calls `spa_set_deadman_ziotime(MSEC2NSEC(zfs_deadman_synctime_ms))`, which is notable and should be checked against upstream intent.
