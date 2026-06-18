# sources/distributed-fs/ceph-client/drivers/md/md-bitmap.h

Purpose: Defines the common MD bitmap on-disk superblock format, bitmap state flags, statistics structure, and operation vtable used by both the original bitmap (`md-bitmap.c`) and lockless bitmap (`md-llbitmap.c`) implementations.

Important APIs/types/functions: `bitmap_super_t` is the 256-byte little-endian persistent header with magic, version, MD UUID, event counters, sync size, state flags, chunksize, daemon sleep, write-behind, reserved sectors, clustered node count, and cluster name. Version constants distinguish host-endian legacy, little-endian, clustered, and lockless formats. `enum bitmap_state` defines `BITMAP_STALE`, `BITMAP_WRITE_ERROR`, lockless first-use/clean/daemon flags, and `BITMAP_HOSTENDIAN`. `struct md_bitmap_stats` normalizes stats used by cluster code and sysfs. `struct bitmap_operations` is the submodule contract for create/load/destroy/flush/write tracking/discard/sync/cluster-slot helpers/stats/sysfs groups.

Control flow: This header has no standalone runtime flow, but its inline helpers gate callers. `md_bitmap_registered()` checks whether a bitmap provider is selected. `md_bitmap_enabled()` verifies a provider and bitmap object are present, then delegates to provider `enabled()`. `md_bitmap_start_sync()` and `md_bitmap_end_sync()` fall back to 1024-sector full-resync chunks when no bitmap is active; otherwise they delegate to the selected bitmap implementation.

State and persistence: The persistent contract is `bitmap_super_t`. Comments document event-counter rules: bitmap `events` must match or be one ahead of MD metadata, and `events_cleared` records the last clean-array bit clearing point used for accepting re-added devices. `sync_size` records the device range covered by resync, with RAID-level-specific interpretation.

Dependencies/integration: Included by MD bitmap providers, clustered MD, and MD core paths that call through `mddev->bitmap_ops`. It depends on MD types (`struct mddev`, `struct md_rdev`) being available via surrounding includes and uses `sector_t`, `struct file`, and `struct attribute_group` from kernel headers.

Risks and test signals: Changes here affect all bitmap providers. Validate ABI/layout stability of the 256-byte superblock, version compatibility, endian handling, fallback sync behavior without a bitmap, and complete initialization of all `bitmap_operations` entries for each provider. Any new operation must be handled by `bitmap_none_ops`, legacy bitmap, lockless bitmap, and clustered callers.
