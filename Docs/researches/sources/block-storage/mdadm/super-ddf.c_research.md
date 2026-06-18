# File Research: sources/block-storage/mdadm/super-ddf.c

Purpose: mdadm external metadata handler for SNIA DDF RAID metadata. It supports DDF containers, virtual disks/subarrays, member metadata loading/writing, mdmon state updates, spare activation, and mdadm reporting/export operations.

On-disk model:
- DDF metadata lives near the end of devices, with an anchor header locating primary and secondary headers plus sections.
- Multi-byte fields are stored big-endian through wrapper types `be16`, `be32`, and `be64`.
- Defines DDF structures for headers, controller data, physical disk records, virtual disk records, VD configuration records, spare assignments, disk data, and bad block logs.
- `struct ddf_super` is the in-memory aggregate. It holds global metadata (`phys`, `virt`, controller, headers), local disk list `dlist`, virtual config list `conflist`, pending-add list, current subarray context, and DDF sizing parameters.

Loading:
- `load_ddf_headers()` reads the anchor from the last 512 bytes, optionally performs extended search in the last 32 MiB, validates CRC/revision, loads primary/secondary headers, and chooses the active header by sequence/openflag.
- `load_ddf_global()` loads controller, physical disk, and virtual disk sections.
- `load_ddf_local()` loads per-device disk data, config records, spare records, and merges VD configs into `conflist`, including secondary BVD records.
- `load_super_ddf()` loads one member device.
- `load_super_ddf_all()` loads a whole running DDF container by inspecting sysfs member devices and choosing the best sequence.

Layout mapping:
- `layout_md2ddf()` converts md RAID levels/layouts to DDF PRL/RLQ/SRL fields.
- `layout_ddf2md()` converts supported DDF layouts back to md array geometry.
- Supported practical mappings include linear/concat, RAID0, RAID1, RAID4, RAID5 left/right/asymmetric/symmetric subset, RAID6 DDF rotating layouts, and RAID10 forms that map to DDF secondary BVD structures.
- Unsupported combinations report explicit errors.

Creation and writing:
- `init_super_ddf()` creates a new DDF container, reserves 32 MiB at the end, initializes headers, controller data, physical disk table, and virtual disk table.
- `init_super_ddf_bvd()` creates a virtual disk inside an existing container.
- `add_to_super_ddf()` adds physical devices to containers; `add_to_super_ddf_bvd()` assigns member extents to a virtual disk.
- `_write_super_to_disk()` writes primary, secondary, and anchor metadata to each device.
- `__write_ddf_structure()` writes header, controller, physical, virtual, config, and disk-data records with CRC updates and openflag transitions.
- `store_super_ddf()` either writes a specific device’s DDF metadata or clears the last search region during cleanup.

Reporting and identity:
- `examine_super_ddf()`, `brief_examine_super_ddf()`, `brief_examine_subarrays_ddf()`, `export_examine_super_ddf()`, `detail_super_ddf()`, and `brief_detail_super_ddf()` implement mdadm display/export paths.
- `uuid_from_ddf_guid()` hashes DDF GUIDs via SHA1.
- `uuid_of_ddf_subarray()` compensates for vendors such as LSI whose volume GUIDs can vary between boots by hashing container GUID, name, and member number.
- `getinfo_super_ddf()` reports container info; `getinfo_super_ddf_bvd()` reports subarray/member info.

Runtime/mdmon behavior:
- `ddf_open_new()` validates new subarrays against metadata and marks broken devices faulty.
- `ddf_set_array_state()` updates consistency and init-state bits.
- `ddf_set_disk()` updates physical disk state and virtual disk state when devices fail or become in-sync.
- `ddf_sync_metadata()` writes pending metadata updates.
- `ddf_process_update()` dispatches metadata updates by DDF magic to physical, virtual, or VD config handlers.
- `ddf_prepare_update()` preallocates memory needed for config updates.
- `ddf_activate_spare()` finds dedicated or global spares for degraded arrays, reserves space, returns mdinfo entries for replacements, and emits VD config metadata updates.

Space and state management:
- `get_extents()` and `find_space()` track used extents per physical disk.
- `reserve_space()` chooses devices with adequate free extents for new subarrays.
- `get_bvd_state()`, `secondary_state()`, and `get_svd_state()` derive DDF optimal/degraded/failed/partially-optimal state from physical disk availability.
- `ddf_update_vlist()` refreshes each disk’s list of virtual disks and spare/global-spare flags.
- `ddf_remove_failed()` compacts failed transitional physical disk records no longer in use.
- `kill_subarray_ddf()` and `_kill_subarray_ddf()` remove virtual disks.

Superswitch integration:
- Exports `struct superswitch super_ddf` with DDF-specific implementations for examine, load, store, create, validate, compare, container content, mdmon hooks, update processing, spare activation, UUID extraction, and default geometry.
- Marks `.external = 1`, `.swapuuid = 0`, `.name = "ddf"`.

Risks and notes:
- This is high-blast-radius metadata code: it writes raw member-device metadata and manages active mdmon updates.
- Correctness relies on CRC validation, endian conversions, careful sequence/openflag handling, and keeping global versus local DDF records synchronized.
- Extended DDF header search exists for hardware that does not place the anchor in the final sector.
- DDF secondary RAID support is deliberately limited; `check_secondary()` only accepts md-compatible RAID10-like BVD layouts.
- `update_super_ddf_dummy()` is a placeholder so mdadm has a non-null update path, but it does not perform real metadata mutation.
