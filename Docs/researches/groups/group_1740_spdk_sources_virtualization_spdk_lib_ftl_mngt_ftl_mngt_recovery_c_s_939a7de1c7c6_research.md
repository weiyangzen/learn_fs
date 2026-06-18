# Group Research: group_1740_spdk_sources_virtualization_spdk_lib_ftl_mngt_ftl_mngt_recovery_c_s_939a7de1c7c6

Scope confirmed against `Docs/research_subset_a.md`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_recovery.c -->
# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_recovery.c

Implements dirty-shutdown recovery for SPDK FTL. The public entry point `ftl_mngt_recover()` runs `g_desc_recovery`, a management-process pipeline that restores band state, P2L checkpoints, NV cache state, trim state, L2P, valid maps, core poller, optional self-test, and final startup.

Important control flow:
- `ftl_mngt_recovery_init()` computes DRAM-bounded L2P snippet size from `l2p_dram_limit`, unlinks stale L2P cache SHM, allocates temporary recovery metadata, and initializes iteration ranges.
- `g_desc_recovery_iteration` reconstructs one L2P slice by loading persisted L2P, initializing seq IDs from trim metadata, replaying NV cache chunk P2L, replaying band P2L, rebuilding valid bits, then persisting the slice.
- Band replay reads tail metadata, validates closed-band P2L CRC, resolves newer sequence IDs, and invalidates stale overlapping P2L entries on open/full bands.
- NV cache replay validates chunk P2L CRC and wins L2P conflicts by sequence ID.
- Trim recovery has normal and shared-memory paths; it can complete in-progress trim metadata from SHM or recover a logged trim transaction from `TRIM_LOG`.

Key dependencies:
- Management process API from `ftl_mngt`.
- Metadata IO from `ftl_md`.
- Band/P2L checkpoint functions from band and P2L modules.
- `ftl_addr_utils.h` for packed/unpacked address load/store.

Notable risks and invariants:
- Checkpoint recovery is explicitly unsupported in `ftl_mngt_recovery_iteration_init_seq_ids()` when `ckpt_seq_id` is nonzero.
- Recovery assumes P2L CRCs and seq IDs are authoritative for conflict resolution.
- Duplicate valid-map hits assert and fail recovery, which is appropriate for metadata corruption.
- Open-band recovery depends on P2L checkpoint region availability and temporarily requeues bands through `shut_bands`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_self_test.c -->
# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_self_test.c

Defines optional startup validation enabled by the `FTL_SELF_TEST` environment variable. The test scans the full L2P in 4096-LBA pinned windows and compares it against `dev->valid_map`.

Important behavior:
- Allocates a temporary bitmap covering base plus NV cache blocks.
- For every non-invalid L2P address, rejects duplicate physical references.
- Checks that every mapped physical address is set in the device valid map.
- Compares counted temporary valid references with `ftl_bitmap_count_set(dev->valid_map)`.

Risk:
- Intended for debugging only; it loads/checks the whole L2P and can be expensive.
- Cleanup is represented both as step cleanup and explicit final cleanup, so ownership depends on normal management-process cleanup semantics.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_self_test.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_shutdown.c -->
# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_shutdown.c

Defines clean and fast shutdown management pipelines. `ftl_mngt_call_dev_shutdown()` selects `desc_fast_shutdown` when `dev->conf.fast_shutdown` is set, otherwise full `desc_shutdown`.

Full shutdown:
- Deinitializes IO path and stops core poller.
- Persists L2P, trims L2P, persists metadata, marks superblock clean, dumps stats.
- Deinitializes L2P/P2L checkpointing and rolls back device startup resources.
- Uses `ftl_mngt_rollback_device` as an error handler.

Fast shutdown:
- Stops IO path and poller.
- Persists only fast metadata state, marks SHM clean, keeps SHM-backed metadata for fast restart.
- Skips full L2P and full metadata persistence.

Risk:
- Correctness depends on the fast-shutdown shared-memory state being invalidated when metadata SHM setup fails elsewhere.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_shutdown.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_startup.c -->
# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_startup.c

Defines FTL startup, first-create startup, clean restore, dirty recovery selection, RPC trim, and rollback orchestration.

Main startup path:
- `ftl_mngt_call_dev_startup()` executes `desc_startup`.
- Common steps validate config, open base/cache bdevs, initialize superblock, pools, bands, IO device/channel, layout, upgrades, metadata, NV cache, valid/trim maps, band metadata, reloc, then choose create or restore mode.
- Create mode clears L2P, initializes bands, persists initial band/chunk metadata, wipes P2L regions, clears trim metadata/log, marks dirty, starts poller, and finalizes.
- Restore mode chooses clean startup if `dev->sb->clean`, otherwise calls dirty recovery.

Trim path:
- `ftl_mngt_trim()` allocates context and runs a one-step management process calling `spdk_ftl_unmap()`.
- User callback is marshaled back to the original thread.

Risk:
- `ftl_mngt_process_trim_cb()` calls `ftl_mngt_fail_step(ctx)` with `ctx` typed as `void *`; it is the same pointer as `mngt`, but the local variable should be used for clarity.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_startup.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_steps.h -->
# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_steps.h

Central declaration header for FTL management-step actions. It exposes startup, shutdown, metadata, layout, L2P, NV cache, trim, P2L checkpoint, self-test, superblock, and rollback functions used by management process descriptors.

Role:
- Provides the common function vocabulary for `ftl_mngt_startup.c`, `ftl_mngt_shutdown.c`, `ftl_mngt_recovery.c`, and related step implementations.
- Keeps management pipelines loosely coupled to implementation files.

Risk:
- Large flat header creates broad compile-time coupling, but it matches the management-process descriptor pattern used in this subsystem.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_steps.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_upgrade.c -->
# File Research: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_upgrade.c

Wraps layout upgrade into management-process steps. `ftl_mngt_layout_upgrade()` calls a process that repeatedly selects the next region requiring upgrade, runs the corresponding region upgrade, persists the superblock, and continues until done.

Important behavior:
- Allocates per-region upgrade context according to descriptor `ctx_size`.
- `region_upgrade_cb()` frees upgrade context, stores the superblock blob area on success, then advances.
- `layout_upgrade()` handles `CONTINUE`, `DONE`, and `FAULT` outcomes from `ftl_layout_upgrade_init_ctx()`.
- On completion it verifies/dumps upgraded layout via `ftl_upgrade_layout_dump()`.

Risk:
- Upgrade context ownership is split across async region callbacks and parent loop; careful cleanup avoids leaks but requires region upgrades to honor callback contracts.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/mngt/ftl_mngt_upgrade.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_bdev_common.c -->
# File Research: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_bdev_common.c

Common helpers for NV cache bdev device types.

Functions:
- `ftl_nvc_bdev_common_is_chunk_active()` dry-runs an insert into the NVC layout tracker to determine whether a chunk-sized range is free/usable.
- `ftl_nvc_bdev_common_region_create()` aligns metadata region size and adds it to the NVC layout tracker.
- `ftl_nvc_bdev_common_region_open()` finds a region of a requested type/version and fills an `ftl_layout_region` descriptor with bdev descriptor, IO channel, VSS size, entry size/count, offset, size, and version.

Risk:
- `region_open()` accepts an existing region if `blk_sz >= requested`, so callers must tolerate larger backing regions.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_bdev_common.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_bdev_common.h -->
# File Research: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_bdev_common.h

Header declaring common NVC bdev layout helpers:
- Chunk active/free check.
- Region create.
- Region open.

It is shared by VSS and non-VSS NVC backends.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_bdev_common.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_bdev_non_vss.c -->
# File Research: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_bdev_non_vss.c

Implements an NV cache backend for bdevs without separate metadata/VSS.

Important behavior:
- Accepts only bdevs with metadata size `0`.
- Initializes/deinitializes P2L log support.
- On chunk open, acquires a P2L log tied to chunk sequence ID; on close, releases it.
- Writes user IO with `spdk_bdev_writev_blocks()`, then logs P2L entries before completing the NV cache write.
- Recovers open chunks by reading P2L logs and rebuilding chunk address mappings.
- Creates and opens P2L log IO layout regions during setup.

Risk:
- `init()` ignores nonzero `ftl_p2l_log_init()` return and still returns `0`, which may hide initialization failure.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_bdev_non_vss.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_bdev_vss.c -->
# File Research: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_bdev_vss.c

Implements an NV cache backend for bdevs with separate metadata carrying VSS records.

Important behavior:
- Requires separate metadata IO, metadata size equal to `union ftl_md_vss`, DIF disabled, and zero buffer large enough for metadata transfers.
- Writes allocate metadata from `nv_cache.md_pool`, fill VSS metadata, and call `spdk_bdev_writev_blocks_with_md()`.
- On write completion, returns metadata buffer to the pool and completes the NV cache write.
- Open-chunk recovery scans chunk data up to tail metadata offset with `spdk_bdev_read_blocks_with_md()`, filters VSS entries by chunk sequence ID, and rebuilds chunk P2L mappings.

Risk:
- Metadata pool exhaustion calls `ftl_abort()`, so pool sizing is a hard correctness precondition.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_bdev_vss.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_dev.c -->
# File Research: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_dev.c

Global registry for NV cache device types.

Behavior:
- Maintains a TAILQ protected by `g_devs_mutex`.
- `ftl_nv_cache_device_register()` validates name and rejects duplicate names by aborting.
- `ftl_nv_cache_device_get_type_by_bdev()` iterates registered types and returns the first whose `is_bdev_compatible()` accepts the bdev.

Risk:
- Selection order is constructor registration order; compatibility predicates must be mutually exclusive or intentionally prioritized.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_dev.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_dev.h -->
# File Research: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_dev.h

Defines the NV cache device-type interface and constructor registration macro.

Interface includes optional operations for:
- Init/deinit.
- Chunk open/close notification.
- Bdev compatibility.
- Chunk active check.
- Write path.
- Periodic processing.
- Open-chunk recovery.
- Backend-specific layout setup.
- Metadata layout operations.

The `FTL_NV_CACHE_DEVICE_TYPE_REGISTER()` macro registers static descriptors at module load via constructor.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/nvc/ftl_nvc_dev.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_band_upgrade.c -->
# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_band_upgrade.c

Defines band metadata region upgrade from v1 to v2.

Behavior:
- Verification requires clean upgrade eligibility and pre-creates/opens the v2 region.
- Upgrade reads old metadata, shifts each `struct ftl_band_md` contents by the new `version` field size, sets `FTL_BAND_VERSION_2`, and requires bands to be only `CLOSED` or `FREE`.
- Persists converted metadata to the v2 region, then calls `ftl_region_upgrade_completed()`.

Risk:
- This is layout-sensitive binary structure conversion; the static assert requires `struct ftl_band_md` to remain exactly one FTL block.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_band_upgrade.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_chunk_upgrade.c -->
# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_chunk_upgrade.c

Defines NV cache chunk metadata upgrade from v1 to v2.

Behavior:
- Requires major-upgrade eligibility and pre-creates/opens a v2 chunk metadata region sized for `chunk_count`.
- Initializes every v2 chunk metadata entry with `ftl_nv_cache_chunk_md_initialize()`.
- Persists the new region and completes layout upgrade.

Important assumption:
- Comments state chunks should be fully drained of user data before this major upgrade, so old metadata contents are not interpreted.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_chunk_upgrade.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_layout_upgrade.c -->
# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_layout_upgrade.c

Core metadata-layout upgrade engine.

Important behavior:
- Defines descriptor table mapping region types to latest versions and per-version upgrade descriptors.
- `ftl_region_upgrade_enabled()` only allows upgrades after clean shutdown and not SHM-clean state.
- `ftl_region_major_upgrade_enabled()` additionally requires `dev->sb->upgrade_ready`.
- `ftl_layout_verify()` validates regions and runs verify callbacks for every outdated region.
- `ftl_region_upgrade()` dispatches one version upgrade.
- `ftl_region_upgrade_completed()` updates superblock layout tracking, entry sizing, and region version, then invokes callback.
- `ftl_superblock_upgrade()` synchronously upgrades SB versions before normal layout work.
- `ftl_layout_upgrade_init_ctx()` walks regions to select the next outdated region.
- `ftl_layout_upgrade_drop_region()` removes deprecated regions from bdev layout tracker.

Risk:
- Some descriptor entries are intentionally empty for non-upgradable/static regions; callers rely on `latest_ver` and `desc` being valid only where upgrades exist.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_layout_upgrade.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_layout_upgrade.h -->
# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_layout_upgrade.h

Public interface for FTL metadata layout upgrades.

Defines:
- Upgrade result enum.
- Verify and upgrade callback types.
- Per-version `ftl_region_upgrade_desc`.
- Per-region descriptor list.
- `ftl_layout_upgrade_ctx`.
- APIs for checking upgrade eligibility, superblock upgrade, layout verification, region upgrade, completion, next-region selection, and latest-version query.

Contract:
- Region upgrade functions are usually asynchronous and must call `ftl_region_upgrade_completed()` when persisted conversion finishes.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_layout_upgrade.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_p2l_upgrade.c -->
# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_p2l_upgrade.c

Defines P2L checkpoint metadata upgrade from v1 to v2.

Behavior:
- Requires major-upgrade eligibility and pre-creates/opens a v2 P2L checkpoint region sized by `layout.p2l.ckpt_pages`.
- Creates heap metadata object for the new region.
- Clears the region with default metadata/VSS and completes upgrade.

Notable TODO:
- Mentions validation for no open bands is still needed.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_p2l_upgrade.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_prev.h -->
# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_prev.h

Defines previous superblock versions used for upgrade compatibility.

Contents:
- Bug-compatible `FTL_SUPERBLOCK_MAGIC_V2`.
- Version constants v0 through v4.
- Packed/size-checked structs for v2, v3, and v5 superblock layouts.
- v3 includes linked metadata layout head; v5 includes blob-area descriptors for NVC layout, base layout, and layout params.

Role:
- Lets upgrade code reinterpret the current superblock memory as older durable formats.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_prev.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_upgrade.c -->
# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_upgrade.c

Defines superblock upgrade descriptors, currently v4 to v5.

Behavior:
- `sb_v4_to_v5_verify()` requires normal region-upgrade eligibility and rejects upgrade if any pending major region upgrade exists.
- Converts v3-style linked metadata layout records into NVC/base layout trackers, excluding fixed/free/deprecated categories.
- `sb_v4_to_v5_upgrade()` validates non-empty old blob area, loads old metadata layout, bumps header to v5, resets v5 blob descriptors, and leaves v5 layout blob empty for later storage.
- Older SB versions v0-v3 are disabled.

Risk:
- The verifier comparison appears suspicious: it treats `reg->current.version <= latest` as “only latest region version found,” but usually older versions are `< latest`; this may need cross-checking with surrounding layout semantics.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_upgrade.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_upgrade.h -->
# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_upgrade.h

Defines `union ftl_superblock_ver`, a packed overlay for common header, old v2/v3/v5 formats, and current superblock.

Used by superblock version-specific upgrade/load code to reinterpret the same superblock DMA buffer according to header version.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_upgrade.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_v3.c -->
# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_v3.c

Helpers for v3 superblock metadata layout.

Behavior:
- Checks v3 magic and empty layout status.
- Validates linked metadata-region pointers stay inside the fixed superblock buffer.
- `ftl_superblock_v3_md_layout_load_all()` walks linked v3 region records, skips free records, rejects fixed/invalid types, detects duplicate versions and loops, and loads the oldest region version per type into `dev->layout`.
- Requires all v3 region types to be found.
- Dumps v3 linked layout records for diagnostics.

Risk:
- Loop detection is based on a sentinel for non-monotonic `df_next`; malformed but monotonic cycles are impossible in bounded superblock memory if overflow checks hold.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_v3.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_v3.h -->
# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_v3.h

Declares v3 superblock helper APIs:
- Magic check.
- Empty layout check.
- Region overflow check.
- Load all metadata regions.
- Dump metadata layout.

Used during old-format load and v4-to-v5 superblock conversion.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_v3.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_v5.c -->
# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_v5.c

Implements v5 superblock blob-area storage, load, layout application, and region-upgrade bookkeeping.

Important behavior:
- Stores three blobs into the SB blob area: NVC layout tracker, base layout tracker, and layout params.
- Validates blob headers are bounded by `blob_area_end`.
- Loads blobs only if stored NVC/base device type names match the current backend names.
- Finds oldest/latest/specific region versions across NVC and base trackers.
- `ftl_superblock_v5_md_layout_upgrade_region()` handles major upgrades by deleting old region and switching to the new allocated region, or minor upgrades by rewriting version in place.
- Applies loaded layout blobs to live `dev->layout`, taking the oldest version per region type, adding placeholders for missing NVC regions, dropping deprecated `DATA_NVC`, and fixing up base-backed regions.

Risk:
- Blob bounds checks are critical; a corrupt blob header can otherwise make layout parsing unsafe.
- Device type name matching protects against applying a layout blob with an incompatible backend.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_v5.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_v5.h -->
# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_v5.h

Declares v5 superblock APIs for:
- Blob-area empty and validation checks.
- Store/load blob area.
- Upgrade one metadata layout region.
- Apply loaded metadata layout to runtime layout.
- Dump v5 metadata layout.

This is the main interface between current superblock format and layout tracker state.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_sb_v5.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_trim_upgrade.c -->
# File Research: sources/virtualization/spdk/lib/ftl/upgrade/ftl_trim_upgrade.c

Defines trim log metadata upgrade from v0 to v1.

Behavior:
- Requires major-upgrade eligibility and pre-creates/opens a v1 trim log region with one `struct ftl_trim_log` entry.
- Creates heap metadata for the v1 region.
- Clears the metadata region, then completes the layout upgrade.

Risk:
- Contains a misleading comment saying “NV cache metadata region - v2”; the actual code upgrades trim log to `FTL_TRIM_LOG_VERSION_1`.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/upgrade/ftl_trim_upgrade.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_addr_utils.h -->
# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_addr_utils.h

Inline helpers for reading/writing packed or unpacked FTL address/LBA arrays.

Behavior:
- If `ftl_addr_packed(dev)` is true, loads/stores 32-bit values and maps 32-bit invalid sentinels to full invalid constants.
- Otherwise uses 64-bit arrays directly.
- Provides symmetric helpers for `ftl_addr` and LBA values.

Risk:
- Store paths assign potentially 64-bit invalid values into 32-bit slots when packed; correctness depends on invalid constants being intentionally compatible.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_addr_utils.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_bitmap.c -->
# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_bitmap.c

Implements a caller-buffer-backed bitmap.

Features:
- Size/block conversion helpers with word alignment.
- Creation validates buffer address and size alignment.
- Get/set/clear by bit index.
- Find-first-set/clear in a range using word scanning and `__builtin_ctzl`.
- Count set bits using `__builtin_popcountl`.

Risk:
- Bounds are enforced by `assert`, so production builds rely on callers passing valid bit ranges.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_bitmap.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_bitmap.h -->
# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_bitmap.h

Public API for FTL bitmaps:
- Buffer alignment constant.
- Bits-to-size and bits-to-blocks helpers.
- Create/destroy.
- Get/set/clear.
- Find first set/clear.
- Count set bits.

The bitmap object owns only its descriptor; the backing buffer is supplied by the caller.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_conf.c -->
# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_conf.c

Configuration defaults, copy/deinit, device initialization, and validation.

Behavior:
- Default config sets GC/free-band thresholds, 20% overprovisioning, 2 GiB L2P DRAM limit, user IO pool size, NV cache compaction/free targets, and fast shutdown enabled.
- `spdk_ftl_conf_copy()` deep-copies pointer strings.
- `ftl_conf_init_dev()` validates required name/base/cache fields, copies config into device, initializes limit, and registers mutable boolean properties.
- `ftl_conf_is_valid()` validates overprovisioning, NV cache thresholds, chunk target, and L2P DRAM limit.

Risk:
- `spdk_ftl_conf_deinit()` frees strings but does not null them, so callers should not reuse the struct after deinit without reinitialization.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_conf.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_conf.h -->
# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_conf.h

Small header declaring:
- `ftl_conf_is_valid()`.
- `ftl_conf_init_dev()`.

Include guard comment says `FTL_DEFS_H`, likely a copy/paste typo.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_conf.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_defs.h -->
# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_defs.h

Common FTL utility definitions.

Contents:
- KiB/MiB/GiB/TiB constants if not already defined.
- `ftl_abort()` assert-plus-abort helper.
- `ftl_bug(cond)` hard abort on unexpected condition.
- Generic invalid values for band IDs and physical IDs.

Role:
- Provides fail-fast invariants used throughout FTL metadata and upgrade code.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_defs.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_df.h -->
# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_df.h

Defines durable-format object IDs as offsets from a base pointer.

APIs:
- `ftl_df_get_obj_id(base, ptr)` returns byte offset.
- `ftl_df_get_obj_ptr(base, id)` reconstructs pointer.

Used for superblock blob/linked structures and external-buffer mempool references.

Risk:
- Pointer/object bounds are not checked here beyond assertions; callers must validate IDs before conversion when reading durable data.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_df.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_layout_tracker_bdev.c -->
# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_layout_tracker_bdev.c

Implements a block-device region tracker for metadata layout allocation.

Behavior:
- Initializes with one free region covering the full bdev.
- Adds regions by best-fit free region, with optional block alignment and splitting.
- Inserts regions at exact block offsets, also supporting dry-run with `FTL_LAYOUT_REGION_TYPE_INVALID`.
- Removes regions and coalesces adjacent free regions.
- Iterates regions by type, or all regions with invalid type filter.
- Serializes allocated regions only into packed blob entries.
- Loads blob entries by resetting the tracker and exact-inserting each allocated region.

Risk:
- `blob_store()` checks capacity before skipping free entries, so many free entries can falsely exhaust a small blob buffer even though they are not serialized.
- Exact insert and remove rely on duplicate `(type, version)` being disallowed, not duplicate physical ranges alone.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_layout_tracker_bdev.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_layout_tracker_bdev.h -->
# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_layout_tracker_bdev.h

Public API for bdev layout tracker.

Defines region properties:
- Type.
- Version.
- Block offset.
- Block size.

Exposes init/fini, add, remove, find-next, blob store/load, and exact insert. Used by NVC/base metadata layout management and superblock v5 blob storage.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_layout_tracker_bdev.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_log.h -->
# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_log.h

FTL logging macros wrapping `spdk_log`.

Behavior:
- Prefixes messages with `[FTL][<dev name>]`, using `N/A` for null device.
- Provides error, warning, notice, info, and debug macros.

Role:
- Standardizes subsystem logging across FTL code.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_log.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_md.c -->
# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_md.c

Core FTL metadata object implementation, including allocation, SHM lifecycle, VSS buffers, async metadata IO, mirror handling, entry IO, clear/persist/restore, and region-specific memory flags.

Important behavior:
- Metadata buffers can be heap, SPDK DMA, or shared memory under `/dev/hugepages/ftl_<uuid>_<name>`.
- SHM creation verifies mode/size, mmaps, mlocks, and registers memory with SPDK.
- `ftl_md_create()` can allocate VSS data after data blocks and per-entry VSS DMA buffers.
- Full metadata IO is chunked by `ftl_md_xfer_blocks()` and uses SPDK bdev APIs, with NV cache wrappers when targeting the NVC bdev.
- Restore copies read data into `md->data`; persist copies from `md->data` into IO DMA buffer.
- Mirror logic persists/clears mirror first, restores from mirror on primary read failure, and resyncs mirror after dirty shutdown restore.
- Entry IO supports persisting/reading individual metadata entries with optional VSS and mirror writes.
- Region flag helpers decide SHM/SPDK/heap allocation and whether fast shutdown keeps SHM.

Risk:
- Uses `void *` pointer arithmetic in several places, relying on compiler extension.
- Many serious failures call `ftl_abort()` rather than returning errors.
- Mirror fallback reads the whole mirror, not granular ranges, as noted by TODO.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_md.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_md.h -->
# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_md.h

Public metadata object API and type definitions.

Defines:
- `struct ftl_md` ownership, buffers, IO state, SHM state, mirror flags.
- `union ftl_md_vss` fixed 64-byte metadata variants for version, trim, P2L checkpoint, and NV cache.
- Create/destroy flags.
- Restore, persist, clear, full-buffer access, VSS allocation, entry read/persist, transfer sizing, and region SHM flag helpers.

Contract:
- Callers set `md->cb` and owner context before async operations.
- Entry operations require `region->entry_size` to be set.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_md.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_mempool.c -->
# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_mempool.c

Custom fixed-size FTL mempool.

Behavior:
- `ftl_mempool_create()` allocates DMA memory and initializes an SLIST free list.
- `get`/`put` pop and push elements after validity assertions.
- External-buffer mode creates an uninitialized pool plus bitmap of claimed durable-format entries.
- Before initialization, callers can claim/release durable-format object IDs; `ftl_mempool_initialize_ext()` builds the free list from unclaimed entries.
- Provides conversions between pool pointers, durable-format offsets, and indices.

Risk:
- `ftl_mempool_is_initialized()` returns `inuse_buf == NULL`; the name is correct for initialized normal mode, but the assertion logic can be easy to misread.
- Pointer arithmetic on `void *` relies on compiler extension.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_mempool.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_mempool.h -->
# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_mempool.h

Header for the FTL fixed-size mempool.

APIs cover:
- DMA-backed pool create/destroy/get/put.
- Externally backed pool create/destroy/initialize.
- Durable-format object claim/release before initialization.
- Pointer/id/index conversion helpers.

The header documents the two-state lifecycle: uninitialized external pools allow claim/release, initialized pools allow get/put.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_mempool.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_property.c -->
# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_property.c

Runtime FTL property registry and JSON-RPC dump/decode/set support.

Behavior:
- Properties are stored in a per-device LIST.
- Registration rejects duplicate names and aborts on allocation failure.
- Dump emits device name and visible properties, including units/descriptions and read-only marker.
- Verbose-only properties are hidden unless `dev->conf.verbose_mode`.
- Decode allocates an output buffer sized to the property, checks access, and invokes the property decoder.
- Set checks access and invokes the property-specific setter.
- Provides bool/uint dump helpers, generic binary-copy setter, and bool string decoder.

Risk:
- Property names are not copied; registered name/unit/description strings must outlive the property.
- `ftl_properties_deinit()` frees `dev->properties` but does not null it.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_property.c -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_property.h -->
# File Research: sources/virtualization/spdk/lib/ftl/utils/ftl_property.h

Public property system API.

Defines:
- Init/deinit.
- Dump helpers for bool, uint64, uint32.
- Callback typedefs for dump, decode, and set.
- Property registration, JSON dump, decode, set, generic setter.
- Inline helper for mutable boolean properties.

Used by FTL config initialization and RPC property handling.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/ftl/utils/ftl_property.h -->

<!-- BEGIN FILE RESEARCH: sources/virtualization/spdk/lib/fuse_dispatcher/Makefile -->
# File Research: sources/virtualization/spdk/lib/fuse_dispatcher/Makefile

Build recipe for SPDK `fuse_dispatcher` library.

Behavior:
- Sets `SPDK_ROOT_DIR` two directories up and includes `mk/spdk.common.mk`.
- Declares shared object version `3.0`.
- Builds `fuse_dispatcher.c` into library `fuse_dispatcher`.
- Adds SPDK include root to `CFLAGS`.
- Uses `fuse_dispatcher.map` as the symbol map.
- Includes `mk/spdk.lib.mk` for standard SPDK library build rules.
<!-- END FILE RESEARCH: sources/virtualization/spdk/lib/fuse_dispatcher/Makefile -->