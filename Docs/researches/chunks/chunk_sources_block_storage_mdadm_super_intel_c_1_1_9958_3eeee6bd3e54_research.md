# Chunk Research: sources/block-storage/mdadm/super-intel.c lines 1-9958

## Scope

This chunk covers mdadm's Intel Matrix Storage Manager (IMSM) metadata implementation: on-disk format definitions, in-memory container state, platform/HBA discovery, metadata load/examine/create/write paths, geometry validation, mdmon state projection, spare activation, and active-array state transitions.

The file continues after this chunk. The boundary cuts through `apply_reshape_container_disks_update()`, whose completion and `imsm_process_update()` dispatcher are in the next chunk.

## APIs And State

- Defines IMSM metadata structs: `imsm_super`, `imsm_disk`, `imsm_dev`, `imsm_vol`, `imsm_map`, `migr_record`, `bbm_log`.
- `struct intel_super` is the main runtime container object, owning raw MPB buffers, migration record buffers, parsed device list, disk lists, missing disks, BBM log, HBA/OROM capability, sector size, and update counters.
- Metadata update payloads are declared for mdmon-driven changes: create/kill/rename array, add/remove disk, activate spare, reshape, takeover, checkpoint, size change, badblock allocation, and RWH policy.
- Core accessors handle variable-length metadata: `get_imsm_map()`, `sizeof_imsm_map()`, `sizeof_imsm_dev()`, `get_imsm_dev()`, disk ordinal helpers, RAID level mapping, and 64-bit split/join helpers.

## Control Flow

- Load path:
  - `load_super_imsm()` rejects partitions, allocates `intel_super`, discovers sector size and platform capability, loads MPB, parses disks/devices, loads BBM, handles 4K conversion, retries mdmon checksum races, and loads migration records.
  - `load_super_imsm_all()` loads all candidate member MPBs, resolves the best family/generation via `imsm_thunderdome()`, merges disk lists, finds missing disks, and rejects unsupported migration metadata.
- Examine/getinfo path:
  - `examine_super_imsm()` prints MPB, disk, volume, BBM, and migration-record details.
  - `getinfo_super_imsm()` and `getinfo_super_imsm_volume()` project IMSM metadata into mdadm `mdinfo`, including layout, consistency policy, PPL/bitmap offsets, resync starts, reshape fields, UUID, and member maps.
  - `container_content_imsm()` builds the mdinfo tree for subarrays and members.
- Create/write path:
  - `init_super_imsm()` creates a fresh container or delegates to `init_super_imsm_volume()`.
  - `add_to_super_imsm()` adds disks as container spares or delegates to volume membership.
  - `write_super_imsm()` serializes disks, devices, BBM log, MPB size/checksum, migration record clearing, 4K conversion, active member writes, and spare metadata writes.
- Runtime mdmon path:
  - `imsm_set_array_state()` handles dirty/clean transitions, init/repair start, resync completion, checkpoint updates, and reshape progress.
  - `imsm_set_disk()` records member failure, rebuild completion, degraded/failed transitions, and migration end.
  - `imsm_activate_spare()` selects replacement disks and builds `update_activate_spare` metadata updates.

## Dependencies

- mdadm internals: `mdadm.h`, `mdmon.h`, `dlink.h`, `platform-intel.h`, `drive_encryption.h`, `sha1.h`, `xmalloc.h`.
- Linux interfaces: `/proc/cmdline`, `/sys/dev/block`, `/sys/block`, md sysfs, mdstat, raw block-device `read/write/lseek/fsync`, SCSI `SG_IO`, NVMe sysfs serial lookup.
- Intel platform/OROM helpers: HBA discovery, VMD/NVMe support checks, RAID level/chunk capability checks, controller path matching.
- PPL/bitmap support uses mdadm PPL structures, CRC32C, and reserved post-volume metadata areas.

## Notable Behavior

- IMSM MPB is stored at the second-to-last sector, with optional extended sectors before it; migration record is stored at the last sector.
- Metadata internally uses 512-byte sector units. 4K-sector devices are normalized through `convert_from_4k()` after reads and `convert_to_4k()` before writes.
- General migration uses map0 as destination, map1 as current/source, and an external `migr_record`.
- Rebuild/init/repair use duplicated maps and `IMSM_ORD_REBUILD` flags in disk order tables.
- UUIDs are synthetic SHA1-derived values from signature, family number, volume index, and volume name.
- PPL and bitmap share the same reserved 1 MiB post-volume area and are mutually exclusive.

## Risks

- Several metadata accessors abort on invalid indexes; malformed metadata can terminate the process rather than returning a load error.
- Variable-length pointer arithmetic depends heavily on sane on-disk counts (`num_disks`, `num_raid_devs`, `num_members`, `mpb_size`).
- 4K conversion mutates the MPB in place; callers must preserve internal 512-sector-unit state.
- `clear_badblock()` returns success even when no matching entry is removed.
- Volume counting and platform-limit checks race live mdstat/sysfs/mdmon state.
- `kill_subarray_imsm()` unlinks a `devlist` entry in the non-mdmon path without freeing it.
- `apply_reshape_migration_update()` limits `subdev` to 0 or 1 and logs `new_disk->index` before checking `new_disk` for NULL.
- Adjacent post-boundary takeover code contains a FIXME about disk index correctness.

## Cross-Chunk References

- `apply_reshape_container_disks_update()` starts at line 9897 and continues after this chunk.
- `apply_takeover_update()` and `imsm_process_update()` are after the chunk boundary and consume update structures/helpers defined here.
- Forward references to later code include `recover_backup_imsm()`, `imsm_prepare_update()`, `imsm_delete()`, later reshape/takeover/bitmap helpers, and final `super_imsm` registration.