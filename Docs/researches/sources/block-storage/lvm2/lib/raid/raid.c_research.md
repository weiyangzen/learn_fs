# File Research: sources/block-storage/lvm2/lib/raid/raid.c

This file defines device-mapper RAID segment types and their handler operations.

Main entry points:
- `_raid_ops`: display, text import/export, target status compatibility, target line generation, percent, target present, transient status, modules needed, dmeventd hooks, destroy.
- `raid_is_available()`.
- Initialization: `init_raid_segtypes()` or shared `init_multiple_segtypes()`.

Behavior:
- Text import accepts either `device_count` or `stripe_count`, reads RAID attributes (`region_size`, `stripe_size`, `data_copies`, recovery rates, writebehind, data_offset), and imports metadata/data LV pairs.
- Text export distinguishes raid0-style `stripe_count`/`raid0_lvs` from parity/mirror `device_count`/`raids`.
- `_raid_add_target_line()` builds `dm_tree_node_raid_params_v2`, including raid type, mirrors/stripes/data copies, region size, stripe size, rebuild bitmap, writemostly bitmap, recovery rates, reshape delta disks, data offset, and `DM_NOSYNC`.
- `_raid_target_percent()` parses device-mapper raid status and updates progress.
- `_raid_transient_status()` validates active kernel dev count, checks meta/data LV existence, marks dead devices as `PARTIAL_LV`, and updates VG partial state.
- `_raid_target_present()` probes raid target version and exposes feature flags for raid10, raid0, shrinking, rebuild+emptymeta, reshape, and raid4 support.
- `raid_is_available()` implements degraded-availability policy for raid0, raid1, raid4/5, raid6, and raid10.

Segment types:
- Registers raid0, raid0_meta, raid1, raid10, raid10_near, raid4, raid5 variants, and raid6 variants.
- raid0/raid0_meta are never monitored; other raid types may get dmeventd DSO monitoring.

Dependencies:
- Device-mapper raid target, text import/export, activation/status, dmeventd, segment allocation and registration, metadata LV classification.

Correctness notes:
- Kernel MD/dm-raid limits area count to `DEFAULT_RAID_MAX_IMAGES`.
- Raid4 support is excluded for target version 1.8 and 1.9.0.
- Raid10 availability checks one live leg per mirror group using current two-copy assumption.
- Import treats `_rmeta_` LVs as optional metadata devices preceding data devices.

Risks:
- Reshape delta plus/minus flags are mutually exclusive and checked at target-line generation.
- Area pair import depends on naming convention `_rmeta_`.
- Feature gating is cached statically, so target version changes during process lifetime are not re-evaluated.
