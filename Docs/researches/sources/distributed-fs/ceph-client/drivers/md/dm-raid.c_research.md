# sources/distributed-fs/ceph-client/drivers/md/dm-raid.c

## Purpose
Implements the modern `raid` device-mapper target backed by the MD RAID personalities. It supports raid0, raid1, raid10, raid4/5/6 variants, optional raid4/5/6 journal devices, rebuilds, resync controls, bitmap region sizing, grow/shrink, reshape, and level takeover while exposing a DM table/status/message interface.

## Important APIs, Types, And Functions
`struct raid_set` is the target context and embeds an `mddev`, selected `raid_type`, runtime/constructor flags, rebuild bitmap, requested layout parameters, optional journal device, and flexible array of `struct raid_dev` members. `struct raid_dev` pairs a metadata device, data device, and `md_rdev`. `struct dm_raid_superblock` is the dm-raid on-disk metadata format, including v1.9 reshape extensions.

Major functions include `raid_ctr()`/`raid_dtr()`, `raid_map()`, `raid_status()`, `raid_message()`, `raid_preresume()`, `raid_resume()`, and suspend hooks. Parsing and validation are split across `parse_raid_params()`, `parse_dev_params()`, `validate_region_size()`, `validate_raid_redundancy()`, `rs_check_takeover()`, and `rs_check_reshape()`. Superblock handling is implemented by `super_load()`, `super_validate()`, `super_init_validation()`, `super_sync()`, and `analyse_superblocks()`. Reshape/takeover flow uses `rs_prepare_reshape()`, `rs_setup_reshape()`, `rs_start_reshape()`, `rs_setup_takeover()`, and size/offset helpers.

## Control Flow
Construction parses `<raid_type> <#raid_params> ... <#raid_devs> <meta data>...`, allocates `raid_set`, parses target options, opens all component devices, computes requested array/device sizes, analyzes superblocks to recover current state, decides whether the table represents a new set, recovery, reshape continuation, takeover, reshape request, grow/shrink, or unchanged set, then initializes and starts the embedded MD array suspended/frozen. RAID I/O is mapped by handing bios to `md_handle_request()`, with requeue for addresses past current MD array size during forward grow reshape.

Resume-time work is important: `raid_preresume()` updates superblocks when needed, loads/resizes the MD bitmap, applies grow capacity, sets recovery windows, and starts requested reshape. `raid_resume()` unfreezes MD recovery and writes, and on secondary resume attempts to restore previously faulty devices. Suspend freezes sync changes, prepares interrupted raid456 reshape if needed, stops writes, suspends MD, and marks the array read-only.

## State And Persistence
Persistent state lives in dm-raid superblocks on metadata devices. The superblock stores magic, compatible feature flags, device count/position, event counter, failed-device bitmap, per-disk recovery offset, array resync offset, level/layout/chunk, reshape flags and position, new layout/chunk/delta, array sectors, data offsets, rdev sectors, and extended failed-device bits. `super_sync()` writes little-endian metadata from current `mddev`/`md_rdev` state.

Volatile state includes constructor flags, runtime flags such as prereresumed/resumed/bitmap-loaded/update-superblocks/reshape/grow/frozen, MD recovery flags, bitmap state, journal mode, and target capacity. The target carefully separates constructor-requested new layout from superblock-current layout until it can decide whether a conversion is legal.

## Dependencies And Integration Points
The target integrates deeply with MD core (`mddev`, `md_rdev`, personalities, bitmaps, recovery thread, reshape APIs), RAID personalities (`raid1`, `raid5`, `raid10`), DM target registration through `module_dm(raid)`, DM table events/status/messages, and block queue limits. Userspace integration is through documented target table parameters and messages such as `frozen`, `idle`, `resync`, `recover`, `check`, and `repair`.

## Risks
This is a high-risk control-plane file: wrong parsing or flag validation can permit unsafe RAID layouts; wrong superblock selection can assemble stale or incompatible arrays; and reshape/grow data-offset mistakes can overwrite live data. The code explicitly disables some operations for degraded, recovering, reshaping, or journaled sets, and those checks must remain conservative. Discard support for raid456 is disabled unless the module parameter asserts safe zeroing semantics. Status and table output must remain userspace-compatible because tools reconstruct arrays from it.

## Test Signals
Coverage should include each RAID level/layout, metadata and metadata-less tables, invalid flag combinations, rebuild paths, failed-device re-add, bitmap loading/resizing, suspend/resume, status/table round-trip, messages for sync actions, raid456 journal modes, grow/shrink, reshape with data offsets, and takeover validation. Fault injection should cover superblock read errors, stale events, failed devices, degraded arrays, interrupted reshape, and discard behavior with `devices_handle_discard_safely` both false and true.
