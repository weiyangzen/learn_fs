# File Research: sources/block-storage/lvm2/tools/lvcreate.c

This file implements `lvcreate` command parsing, validation, size calculation, VG processing, and final delegation to the common LVM LV creation library. It supports standard linear/striped LVs, mirrors, RAID, snapshots, thin volumes/pools, cache volumes/pools, VDO volumes/pools, and helper flows that create an LV then attach cache/writecache using `lvconvert` functions.

Core data flow:
- `struct lvcreate_cmdline_params` stores raw command-line size, virtual size, percent mode, and PV arguments before VG-dependent conversion.
- `struct processing_params` passes `lvcreate_params` plus command-line parameters through `process_each_vg()`.
- `_lvcreate_params()` is the main command-line parser. It selects the segment type, validates compatible option sets, reads zero/wipe settings, parses names, sizes, stripes, pool/cache/VDO/mirror/RAID options, allocation policy, and tags.
- `_lvcreate_single()` runs after opening the VG. It reads activation settings, resolves ambiguous snapshot/cache/pool cases, performs final VG-dependent validation and extent calculations, prepares lockd state, then calls `lv_create_single()`.

Name and syntax parsing:
- `_lvcreate_name_params()` resolves VG name, LV name, pool name, origin name, and ambiguous positional syntax.
- Cache creation syntax is special: a positional `vg/lv` can mean an existing cache pool or an origin that should be cached, and `_determine_cache_argument()` decides after the VG is open.
- Snapshot syntax distinguishes classic COW snapshots from thin snapshots in `_determine_snapshot_type()`.
- Pool-style commands allow `--name` to name the pool and guard against the same name being used for both pool and LV.

Size and extent handling:
- `_read_size_params()` enforces mutually exclusive `--size` and `--extents`, rejects invalid negative/zero values, and allows size omission only for snapshots/thin cases where another rule supplies meaning.
- `_update_extents_params()` converts sizes and percentages into extents after the VG is known. It handles `%VG`, `%FREE`, `%PVS`, `%ORIGIN`, mirror image division, stripe-boundary rounding, snapshot COW maximum sizing, VDO maximum pool size, and pool metadata reservation.
- Pool creation updates thin/cache pool metadata extents and chunk sizes using `update_thin_pool_params()` or `update_cache_pool_params()`.

Segment-specific validation:
- Mirror and RAID parsing is split across `_read_mirror_params()`, `_read_raid_params()`, and `_read_mirror_and_raid_params()`.
- RAID validation enforces minimum stripes, RAID10 mirror/stripe rules, RAID6 `--nosync` prohibition, recovery rate ordering, RAID0/RAID4/RAID10 target feature support, region-size minimums, and optional RAID integrity settings.
- Thin validation ensures a consistent final state among thin LV, thin pool, snapshot, origin, and pool parameters.
- Cache validation reads cache mode, policy, metadata format, and settings.
- VDO validation reads target settings, handles pool header sizing near maximum virtual size, and checks VDO constraints after extents are known.
- `_check_zero_parameters()` disables or rejects zeroing when the target cannot be zeroed, the LV is read-only/inactive/activation-skipped, or an origin is involved.

Pool handling:
- `_check_pool_parameters()` validates pool-only options, pool name existence, pool type compatibility, persistent major/minor restrictions for pools, and whether pool metadata options are legal.
- For pool creation, `_lvcreate_single()` ensures a pool metadata spare with `handle_pool_metadata_spare()` before calling `lv_create_single()`, and removes a newly created spare on failure when possible.

Activation and locking:
- `_read_activation_params()` parses activation mode, error-when-full behavior, readahead with page-size alignment, persistent major/minor, activation-skip flags, and autoactivation.
- `_lvcreate_single()` uses `lockd_lvcreate_prepare()` and `lockd_lvcreate_done()` around `lv_create_single()`.

Create-and-attach helpers:
- `_lvcreate_and_attach_cmd()` creates a normal linear/striped LV while ignoring the user-visible `--type`, then attaches a cache or writecache by calling a supplied attach function.
- `lvcreate_and_attach_writecache_cmd()` reuses `lvconvert_writecache_attach_single()`.
- `lvcreate_and_attach_cache_cmd()` reuses `lvconvert_cachevol_attach_single()`.
- If attach fails, `_lvcreate_and_attach_single()` deactivates and removes the newly created LV with dependencies.

Important implementation notes:
- The parser uses explicit option allowlists/disallowlists per segment type, making this file the first line of defense against unsupported combinations.
- Many decisions are deferred until VG open because existing LV names and types determine whether syntax means pool creation, cache attachment, classic snapshot, or thin snapshot.
- `lvcreate.c` does not itself implement low-level allocation; it normalizes and validates user intent, then delegates to metadata/library helpers.
