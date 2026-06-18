# File Research: sources/block-storage/mdadm/Grow.c

This file implements most of `mdadm --grow`: online array shape changes, component-size changes, linear array extension, internal/clustered/lockless bitmap changes, PPL consistency-policy changes, reshape continuation, backup/restore of reshape critical sections, and container-wide reshapes for external metadata.

Main public entry points:
- `restore_backup()` rebuilds a critical reshape section after interruption, using either external metadata `recover_backup()` or native `Grow_restart()`.
- `Grow_Add_device()` extends active linear arrays by preparing metadata on the new device, issuing `ADD_NEW_DISK`, then updating existing member superblocks.
- `Grow_addbitmap()` adds or removes internal, clustered, or lockless bitmaps, validating array level, bitmap size, PPL conflicts, clustered RAID10 constraints, write-mostly incompatibility, and sysfs bitmap-location support.
- `Grow_consistency_policy()` switches RAID5 arrays between resync and PPL consistency policy, updates external subarray metadata when needed, writes initial PPL areas, and sets sysfs `consistency_policy`.
- `Grow_reshape()` is the top-level shape-change orchestrator. It validates requested size/level/layout/chunk/raid-disks/data-offset combinations, freezes arrays or containers, applies metadata-side checks, updates size if requested, and delegates actual reshape work to `reshape_array()` or `reshape_container()`.
- `Grow_continue_command()` and `Grow_continue()` resume interrupted reshapes from CLI or boot/systemd continuation paths.
- `Grow_restart()` restores backed-up critical sections from a backup file or spare-device backup area, verifies backup metadata checksums/UUID/timestamps, restores stripes, and advances reshape progress in superblocks.
- `make_backup()` and `locate_backup()` manage mdadm’s backup-file symlink naming under `MAP_DIR`.

Reshape planning:
- `analyse_change()` is the core compatibility and transformation planner. It validates RAID level transitions and computes intermediate reshape level, before/after data-disk counts, before/after layouts, parity count, backup block requirements, minimum data-offset movement, and new logical size.
- It handles RAID1 to RAID0/RAID5, RAID10 to RAID0 or RAID10 reshapes, RAID0 to RAID10/RAID4/5/6, RAID4/5/6 conversions, RAID5 to RAID1 for two-device arrays, RAID6 layout preservation/normalization, and immediate no-restripe cases.
- `compute_backup_blocks()` computes the least-common-multiple-sized critical section that aligns to both old and new stripe geometry.
- `remove_disks_for_takeover()` selects one working disk per mirror-copy group when converting RAID1/RAID10 to RAID0 and removes the remaining devices from the active set.
- `reshape_super_size()` and `reshape_super_non_size()` wrap external metadata callbacks so size-only changes can be rolled back but non-size changes are treated as committed metadata changes.

Kernel/sysfs orchestration:
- The file uses md sysfs attributes heavily: `component_size`, `array_size`, `chunk_size`, `layout`, `new_level`, `raid_disks`, `new_offset`, `sync_action`, `sync_min`, `sync_max`, `sync_completed`, `reshape_position`, `suspend_lo`, `suspend_hi`, `reshape_direction`, `array_state`, `stripe_cache_size`, `bitmap/location`, `ppl_sector`, `ppl_size`, and `consistency_policy`.
- `freeze()`, `unfreeze()`, `freeze_container()`, and `unfreeze_container()` stop background resync/recovery or block mdmon-managed external containers before multi-step changes.
- `start_reshape()` sets suspend ranges, sync bounds, and starts sysfs `sync_action=reshape`; `abort_reshape()` stops reshape and resets suspend/sync state.
- `verify_reshape_position()` compares metadata reshape progress with md’s sysfs position to detect stale metadata or unsafe continuation.
- `set_new_data_offset()` tries to avoid user-space backup by moving component data offsets, checking all member superblocks for head/tail room and writing per-device `new_offset`.
- `raid10_reshape()` handles RAID10 separately because RAID10 reshape is driven by data-offset movement rather than mdadm critical-section backup.

Backup and monitoring:
- `struct mdp_backup_super` describes on-disk backup metadata, including magic, set UUID, timestamp, backup device offsets, array offsets, lengths, and checksums. Two global aligned instances, `bsb` and `bsb2`, are used for write/read verification.
- `reshape_prepare_fdlist()` opens active source devices and spare/backup destinations, recording data offsets.
- `reshape_open_backup_file()` creates and sizes a backup file, rejects files on the same raw array device, fsyncs it, and records a symlink in `MAP_DIR` when appropriate.
- `reshape_array()` is the main worker. It validates spares, imposes intermediate levels and shape, adds devices, chooses between data-offset reshape and backup-file/spare backup, forks or delegates to systemd, starts reshape, and monitors to completion.
- `handle_forking()` either continues in an already forked worker, asks systemd to continue, or forks a child.
- `progress_reshape()` is the safety controller for a running reshape. It advances `sync_max`, manages suspend regions, reads `sync_completed`, converts per-device progress back to array progress, and decides when more backup is needed, when reshape completed, or when it aborted.
- `grow_backup()` saves stripes to backup destinations and writes backup-superblocks before and after the data area.
- `forget_backup()` clears backup metadata when a backed-up section is no longer needed.
- `child_monitor()` performs native metadata reshape monitoring: alternates backup slots for sliding-window reshapes, calls `progress_reshape()`, saves/restores suspension state, optionally validates backup data under `MDADM_GROW_VERIFY`, and eventually releases sync limits.
- `validate()` is a regression-test-only backup verifier that compares backup contents with array data.

External metadata and containers:
- External metadata is integrated through `struct supertype` callbacks: `reshape_super`, `manage_reshape`, `recover_backup`, `container_content`, `sync_metadata`, `write_init_ppl`, `kill_subarray` indirectly elsewhere, and update queues via `st->update_tail`.
- `prepare_external_reshape()` loads the container, rejects blocked volumes/container reshapes, rejects PPL or bitmap consistency policies, and enables mdmon update queuing when mdmon is active.
- `reshape_container()` forks a background container reshape manager. It loops over container content, finds each active member array with `reshape_active`, opens it, initializes sysfs, and calls `reshape_array()` for one member at a time.
- External metadata paths ping or start mdmon, flush mdmon updates, and reload container metadata before final level changes or array-size updates.

Important implementation notes:
- Size changes are intentionally separated from shape changes; the file rejects component-size changes combined with chunk/level/layout/raid-disk changes.
- Bitmap and PPL interactions are guarded: PPL cannot be enabled during reshape, bitmaps conflict with PPL, and bitmaps often must be removed before size/shape/level changes when the kernel returns `EBUSY`.
- The code contains compatibility workarounds for old kernels, including suspend range reset ordering, v0.90 2TB component limits, `sync_completed` reset behavior, and missing or restrictive `new_offset` support.
- Error handling is conservative before starting reshape, but once metadata/shape changes begin, rollback is limited. Size-only external metadata changes attempt rollback; non-size external changes explicitly do not.
- This file is tightly coupled to mdadm core helpers in `mdadm.h`, sysfs helpers, metadata backends, mdmon, mdstat parsing, stripe save/restore code, map-file backup naming, and kernel md ioctl/sysfs semantics.
