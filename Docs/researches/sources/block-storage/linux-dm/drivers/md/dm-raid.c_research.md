# File Research: sources/block-storage/linux-dm/drivers/md/dm-raid.c

## Purpose

`dm-raid.c` implements the Device Mapper `raid` target for MD-backed RAID0, RAID1, RAID10, RAID4, RAID5, and RAID6 mappings. It parses DM table syntax, owns the MD `mddev` lifecycle, manages component metadata devices and data devices, supports array activation, recovery, resize, reshape, takeover between compatible RAID levels, optional RAID4/5/6 journal devices, status output, and runtime sync-action messages.

## Core Model

`struct raid_set` is the target context. It embeds an MD `struct mddev`, the selected `raid_type`, constructor/runtime flags, requested disk counts and layout parameters, computed array/device sizes, optional RAID456 journal device state, and a flexible array of `raid_dev` entries. Each `raid_dev` owns a metadata `dm_dev`, data `dm_dev`, and MD `md_rdev`.

The target maintains separate constructor flags for options such as `sync`, `nosync`, `rebuild`, `daemon_sleep`, recovery-rate limits, RAID1 write-mostly/write-behind, RAID456 stripe cache, bitmap region size, RAID10 copies/format, `delta_disks`, `data_offset`, `journal_dev`, and `journal_mode`. Valid flags are constrained per RAID level.

## Table Parsing And Validation

Constructor syntax is:

`<raid_type> <#raid_params> <raid_params...> <#raid_devs> [<meta_dev> <data_dev>]...`

The parser validates chunk size, RAID-specific options, duplicate options, mutual exclusions such as `sync`/`nosync` and `rebuild` with sync directives, recovery-rate ordering, RAID10 copies/format, reshape disk deltas, data-offset alignment, journal-device size, and journal-mode dependency on `journal_dev`.

Device parsing supports `- -`, `- <data_dev>`, and `<meta_dev> <data_dev>`, but rejects `<meta_dev> -`. Metadata availability determines whether the MD array is persistent or external. Rebuild devices are marked out-of-sync with recovery offset zero, while normal devices start as in-sync until metadata overrides them.

## Metadata And Assembly

The DM RAID superblock uses magic `DM_RAID_MAGIC` and little-endian fields for array events, failed-device bitmaps, disk recovery offset, array resync offset, level, layout, chunk sectors, and v1.9 metadata extensions for reshape state, new layout, delta disks, array sectors, data offsets, device sectors, and extended failed-device bits.

`analyse_superblocks()` reads metadata devices, chooses the freshest superblock by event count, initializes new superblocks for first-use or rebuild devices, validates compatible/incompatible feature flags, restores recovery and reshape state, checks device reordering rules, marks failed devices, validates redundancy, and configures bitmap placement unless the set is RAID0 or journaled RAID456.

## Resize, Reshape, And Takeover

The file distinguishes first-use arrays, recovering arrays, ongoing reshapes, requested takeovers, requested reshapes, growth, shrink, and unchanged reloads. Takeover validation encodes allowed MD personality conversions, including selected RAID0/1/4/5/6/10 transitions and RAID10 layout restrictions.

Reshape support covers disk add/remove, layout changes, chunk-size changes, RAID1 mirror count changes, and out-of-place reshape using `data_offset`/`new_data_offset`. `rs_prepare_reshape()`, `rs_setup_reshape()`, and `rs_start_reshape()` coordinate constructor intent with MD personality `check_reshape` and `start_reshape`, update superblocks before reload-sensitive transitions, and adjust capacity before/after disk removal or growth.

## I/O, Suspend, Resume, And Status

`raid_map()` submits bios to MD with `md_handle_request()`, but requeues bios beyond current `mddev->array_sectors` during add-disk reshape. The target advertises one flush bio and conditionally one discard bio; RAID456 discard is disabled unless all devices support discard and the module parameter `devices_handle_discard_safely` is set.

`raid_preresume()` updates superblocks, loads dirty bitmaps, applies growth, resizes bitmaps, seeds recovery state, and starts reshape if requested. `raid_resume()` unfreezes recovery, resumes MD, and can attempt to restore previously faulty devices. `raid_postsuspend()` stops writes and suspends MD.

Status reports table reconstruction, IMA fields, health characters, sync/reshape progress, sync action, mismatch count, data offset, and journal status. Messages drive MD sync actions: `idle`, `frozen`, `resync`, `recover`, `check`, and `repair`.

## Invariants And Risks

- Metadata superblocks are authoritative unless constructor flags deliberately force sync/rebuild/new layout handling.
- `FirstUse` must be cleared before `md_run()` and superblocks must be updated before bitmap load when new devices or layout changes exist.
- `RT_FLAG_*` state gates one-time preresume/resume work, bitmap loading, superblock updates, reshape start, suspension, sync status, and growth.
- RAID10 layout math and reshape constraints are sensitive to near/far/offset copies and disk-count divisibility.
- RAID456 journaled sets cannot be reshaped or taken over.
- Discard on RAID456 is intentionally conservative because discard-zeroing uncertainty can corrupt parity assumptions.
- Capacity changes must occur at the correct point relative to forward/backward reshape to avoid I/O past component end.

## Test Focus

Test constructor grammar, invalid option combinations per RAID level, metadata/no-metadata cases, rebuild devices, failed-device superblock bits, first-use creation, old metadata upgrade, RAID10 format/copy validation, takeover matrix, grow/shrink reloads, out-of-place reshape offsets, interrupted reshape restart, RAID456 journal modes, discard gating, bitmap resize, suspend/resume idempotence, faulty device restoration, status/table/IMA output, and sync-action messages.
