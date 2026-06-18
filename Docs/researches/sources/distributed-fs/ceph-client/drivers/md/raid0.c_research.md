# sources/distributed-fs/ceph-client/drivers/md/raid0.c

## Purpose
`raid0.c` implements the Linux MD RAID0 personality: a striped block device with no redundancy. It builds the run-time strip-zone map from component device sizes, maps each incoming bio to exactly one member device, handles discard fan-out across stripes, reports status, fails the whole array on member failure, and supports limited takeover from degraded RAID4/5, RAID10, and RAID1 layouts.

## Important APIs, Types, And Functions
The file registers `raid0_personality` with MD through `register_md_submodule()`. Its main personality callbacks are `raid0_run`, `raid0_make_request`, `raid0_status`, `raid0_size`, `raid0_takeover`, `raid0_quiesce`, `raid0_error`, and `raid0_free`. `create_strip_zones()` is the central setup routine; it allocates `struct r0conf`, `strip_zone[]`, and the flattened zone-by-disk `devlist`. `find_zone()` converts an array sector into a zone-relative sector. `map_sector()` maps a zone-relative sector to a component `md_rdev` and device-relative offset. `raid0_map_submit_bio()` remaps normal reads/writes/write-zeroes and submits the clone/current bio. `raid0_handle_discard()` translates a discard range into per-device discard bios. Takeover helpers adjust `mddev` geometry before creating the RAID0 config.

## Control Flow
Startup rejects missing chunk size and arrays with bitmaps, applies queue limits for non-DM MD devices, then creates strip zones unless takeover already supplied `mddev->private`. Zone creation rounds each rdev size down to a chunk multiple, counts unique device-size bands, verifies slot coverage, makes the first zone contain all disks, and creates later zones only from devices that extend beyond the previous smallest device. Multi-zone arrays must use either `RAID0_ORIG_LAYOUT` or `RAID0_ALT_MULTIZONE_LAYOUT`; if the superblock and `raid0.default_layout` do not specify one, assembly is refused because Linux 3.14 changed historical layout behavior.

The request path handles flush through `md_flush_request()`, dispatches discard to `raid0_handle_discard()`, splits normal bios at chunk boundaries, then remaps to the selected rdev. The original layout maps multizone sectors using the absolute bio sector for disk rotation compatibility; the alternate layout maps using the zone-relative sector. Broken member devices cause `bio_io_error()` and `md_error()`. Discards may be split at zone boundaries and then decomposed into per-disk ranges based on stripe index, disk index, `disk_shift`, and `dev_start`.

## State And Persistence
Persistent RAID0 state lives in MD metadata outside this file: level, layout, raid disks, chunk sectors, device offsets, and component sizes. In-memory state is `struct r0conf`, which stores zone boundaries, device-start offsets, layout choice, and the rdev lookup table. `create_strip_zones()` mutates `rdev->sectors` to a chunk-aligned value and takeover paths update `mddev->new_*`, `raid_disks`, `delta_disks`, `resync_offset`, and unsupported feature flags. RAID0 has no bitmap, journal, parity log, or recovery persistence because any member loss breaks the array.

## Dependencies And Integration Points
This file integrates with MD core (`md.h`), queue-limit stacking, integrity registration, bio splitting/submission, discard helpers, trace remap events, and RAID5 layout constants for takeover. It depends on `raid0.h` for `struct r0conf`, `struct strip_zone`, and layout enum definitions. It participates in module aliasing as MD personality 2 and exposes the `raid0.default_layout` module parameter.

## Risks
The highest-risk logic is multizone mapping compatibility: wrong layout selection or `disk_shift` math remaps sectors to different disks and can corrupt existing arrays. Zone construction assumes unique size bands and complete raid-disk slot coverage; takeover paths intentionally rewrite geometry and must only run under MD's reshape/takeover constraints. Discard range math differs from normal bio mapping and can silently discard wrong sectors if start/end disk-index calculations regress. RAID0 marks the array broken on member failure, so error handling is intentionally terminal rather than recoverable.

## Test Signals
Useful signals are MD RAID0 creation and assembly tests with equal and unequal device sizes, explicit `raid0.default_layout=1/2`, fio/readback across chunk and zone boundaries, discard verification with devices that support and do not support discard, queue-limit checks, integrity registration, and takeover tests from the supported degraded RAID4/5/10/1 configurations. Regression tests should compare known data patterns before and after reload because the most serious bugs are deterministic remapping errors.
