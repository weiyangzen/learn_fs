# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/dm-vdo-target.c

## Purpose
Implements the Linux device-mapper target named `vdo`. It parses dmsetup table lines into `device_config`, constructs or reuses a VDO instance, maps incoming bios into the VDO data path, exposes status and messages, coordinates suspend/resume/load/grow administrative phase machines, and registers/unregisters the target module.

## Important APIs, Types, And Functions
The device-mapper surface is `vdo_ctr()`, `vdo_dtr()`, `vdo_map_bio()`, `vdo_io_hints()`, `vdo_iterate_devices()`, `vdo_status()`, `vdo_message()`, `vdo_presuspend()`, `vdo_postsuspend()`, `vdo_preresume()`, and `vdo_resume()`, collected in `struct target_type vdo_target_bio`.

The table parser is built from `get_version_number()`, `parse_device_config()`, `parse_optional_arguments()`, `parse_key_value_pairs()`, `parse_thread_config_string()`, `parse_memory()`, `parse_slab_size()`, and boolean/key-value helpers. Table versions 0 through 4 are accepted; older unused fields are skipped for compatibility. Optional settings include deduplication, compression, sparse index, index memory, slab size, max discard blocks, and VDO thread counts.

Administrative flow is encoded by `enum admin_phases` and `ADMIN_PHASE_NAMES`. `perform_admin_operation()` serializes admin work with `admin->busy`, launches a `vdo_completion`, and waits for callback completion. Major phase callbacks are `pre_load_callback()`, `load_callback()`, `suspend_callback()`, `resume_callback()`, `grow_logical_callback()`, and `grow_physical_callback()`, with error handlers for load and growth.

Instance identity is managed by `struct instance_tracker` plus `allocate_instance()`, `release_instance()`, and a growable bitmap. Existing active VDOs are found by device name or backing device through the global VDO registry helpers.

## Control Flow
Construction begins in `vdo_ctr()`. If no running VDO has the DM device name, `construct_new_vdo()` allocates an instance number, parses the table, calls `vdo_make()`, and runs `PRE_LOAD` phases. Pre-load either formats a new layout by clearing layout and saving super/geometry blocks or loads existing super block data and calls `decode_vdo()`. `decode_vdo()` decodes component states, validates block map age, enables read-only handling, and constructs the recovery journal, slab depot, block map, physical zones, logical zones, and hash zones.

If a VDO with the same name already exists, `update_existing_vdo()` parses a new config and `prepare_to_modify()` validates immutable fields, prepares block-map growth, and prepares physical growth layout/slabs when allowed.

`vdo_preresume_registered()` is the main activation path. A pre-loaded VDO runs `LOAD` phases: start loading, open the recovery journal, load or repair the slab depot, mark the volume dirty, initialize block map from journal, prepare allocator, scrub unrecovered slabs, and enable compression/deduplication. Then pending logical and physical grows are applied. If the VDO is not already normal, `RESUME` phases resume dedupe, depot, journal, block map, logical zones, packer, flusher, and data_vio pool.

Suspension is split between `vdo_presuspend()` choosing saving vs no-flush suspending and `vdo_postsuspend()` running `SUSPEND` phases. These drain packer, data_vios, dedupe hash zones, flusher, logical zones, block map, recovery journal, slab depot, wait for read-only transitions, and optionally write clean component state.

Bio mapping is straightforward: flush/prefush bios go to `vdo_launch_flush()`, other bios go to the data_vio pool through `vdo_launch_bio()`. A guard rejects re-entry from a VDO-owned work queue to avoid deadlock.

## State And Persistence
Persistent state is primarily geometry and super block component data, recovery journal state, slab depot state, block map state, and layout partitions. This file drives when that state is written: initial format, load dirtying, suspend clean save, resume dirty save, and grow commits. Runtime state includes active `device_config` objects, VDO admin state, processing-message flag, instance bitmap, thread/device registration, and pending `next_layout` or block-map growth preparation.

Logical growth persists by updating `states.vdo.config.logical_blocks`, saving components, then growing the block map. Physical growth persists by copying journal and slab summary partitions to the new layout, replacing `vdo->layout`, updating physical block count and depot size, saving components, then enabling new slabs.

## Dependencies And Integration Points
This file is the integration hub for Linux device-mapper, block layer queue limits, dm-kcopyd, module parameters, VDO registries, thread registry, admin-state helpers, completion infrastructure, encodings, recovery journal, slab depot, block map, data_vio pool, flush path, dedupe, dump, repair, and message statistics.

User-visible integration includes dmsetup table syntax, `dmsetup status`, `dmsetup table`, `dmsetup message stats`, `config`, `dump`, `dump-on-shutdown`, `compression on/off`, and dedupe index messages. Kernel integration includes `dm_register_target()` in `vdo_init()` and `dm_unregister_target()` in module teardown.

## Risks
The highest risks are admin phase ordering and persistence ordering. Marking the VDO dirty/clean at the wrong time, draining components in the wrong order, or committing growth metadata before copies/slab preparation are safe can lead to recovery failures or read-only entry. Error handling intentionally enters read-only mode in many cases, so tests must verify both success and degraded paths.

Table compatibility is another risk. Version-specific argument counts and skipped legacy fields must remain synchronized with tools. Thread count validation requires logical, physical, and hash zones to be all zero or all non-zero; cache-size validation depends on logical-zone count.

Concurrent lifecycle and message handling are controlled by `admin->busy` and `processing_message`. Races around table reloads, multiple target references to one VDO, and backing-device changes are sensitive. The singleton target feature prevents multiple targets, but the code still handles multiple `device_config` references for reloads.

## Test Signals
Compile with `CONFIG_DM_VDO` and run dmsetup create/load/reload/resume/suspend/remove flows across table versions and optional arguments. Runtime signals include successful status/table/config/stats messages, correct queue limits, flush/discard behavior, no bio submission from VDO-owned queues, successful clean suspend and dirty resume, read-only transition on injected load errors, logical and physical growth across suspend/resume, and no leaked instance numbers or device references on module unload.
