# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/dht-diskusage.c

## Purpose

`dht-diskusage.c` maintains per-subvolume free-space and free-inode telemetry and chooses substitute placement targets when the hashed target is too full. It supports create/migration placement decisions and emits warnings/events when bricks cross configured disk or inode thresholds.

## Important APIs, Types, and Functions

`dht_du_info_cbk` consumes child `statfs` results and updates `conf->du_stats[]` with available percent, bytes, inode percent, chunk count, total/available blocks, and fragment size. `dht_get_du_info` periodically refreshes all child subvolumes using root-gfid `statfs` calls and `GF_INTERNAL_IGNORE_DEEM_STATFS`; `dht_get_du_info_for_subvol` refreshes one indexed child. `dht_is_subvol_filled` checks `min_free_disk` and `min_free_inodes` against either percent or absolute bytes depending on `conf->disk_unit_percent`. `dht_free_disk_available_subvol`, `dht_subvol_with_free_space_inodes`, and `dht_subvol_maxspace_nonzeroinode` select usable alternatives.

## Control Flow

Refresh starts from `dht_get_du_info`, which copies the caller frame, initializes a DHT local, sets a statfs request dict, then winds `statfs` to each child. Each callback updates only the slot whose `prev` cookie matches `conf->subvolumes[i]`, decrements `local->call_cnt`, and destroys the copied frame on the last callback. Placement selection loads the parent directory layout, locks `conf->subvolume_lock`, first searches for a child satisfying both free-space and inode minimums, then falls back to the maximum-space child with nonzero inodes. Candidate filtering rejects ignored rebalance source, layout-error children, and decommissioned bricks.

## State and Persistence Behavior

The file updates only runtime state in `dht_conf_t`: `du_stats[]`, `last_stat_fetch`, and rate-limited per-child `du_stats[i].log` counters. No on-disk layout or file metadata is written here. Space calculations are derived from child `struct statvfs`; inode-free percent is set to 100 when `f_files` is zero to represent dynamically allocated inode filesystems.

## Dependencies and Integration Points

It depends on DHT config/layout helpers, Gluster frame winding, `statfs`, dict APIs, logging, and `gf_event` for `EVENT_DHT_DISK_USAGE` and `EVENT_DHT_INODES_USAGE`. It integrates with create/rebalance placement through `dht_free_disk_available_subvol` and with layout code because candidates must be present and healthy in the relevant directory layout.

## Risks and Test Signals

Important edge cases include stale `du_stats` when refresh frames cannot be allocated, integer truncation in percent computations, division by block size when deriving 1 MiB chunks, absolute-vs-percent threshold confusion, and the subtle use of `i` after unlocking in `dht_is_subvol_filled`. Candidate selection currently chooses a child when either inode percent or space is greater than the running maximum, so tests should cover mixed inode/space pressure. Test signals include mocked `statfs` results, threshold event emission, decommissioned-brick exclusion, layout-error exclusion, refresh throttling by `refresh_interval`, dynamic-inode filesystems, and create fallback to hashed subvol when no alternative qualifies.
