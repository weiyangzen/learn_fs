
# sources/distributed-fs/ceph-client/drivers/md/dm-linear.c

## Purpose
Implements the device-mapper `linear` target: a simple remapping layer that maps a contiguous logical target range onto a contiguous range of one underlying block device. It is a foundational target used directly by dm tables and by other targets as the simplest example of target construction, status, ioctl forwarding, zoned reporting, and DAX passthrough.

## Important APIs, Types, And Functions
`struct linear_c` stores the backing `dm_dev` and starting sector. `linear_ctr()` parses `<dev_path> <offset>`, opens the backing device with the table mode, and configures flush/discard/secure erase/write zeroes counts. `linear_map_sector()` applies `dm_target_offset()`. `linear_map()` rewrites the bio device and sector and returns `DM_MAPIO_REMAPPED`. `linear_status()` emits table and IMA state. `linear_prepare_ioctl()` forwards ioctls only when the target covers the full underlying device from sector zero. Optional hooks include `linear_report_zones()` and DAX direct-access, zero, and recovery-write wrappers. `linear_target` registers the target through `dm_linear_init()`/`dm_linear_exit()`.

## Control Flow
Construction validates two arguments, allocates context, stores the start sector, opens the device, and attaches context to `ti->private`. Runtime bio mapping is synchronous and stateless: calculate target offset, set `bio->bi_bdev`, update `bi_sector`, and return. Zoned and DAX operations translate the target position and delegate to the lower device. Destruction drops the device reference and frees context.

## State And Persistence
Only per-target runtime state exists: the backing device reference and starting sector. There is no on-disk metadata. Persistence and data ordering are inherited from the underlying block device; flushes bypass mapping because the target has a single lower device.

## Dependencies And Integration Points
Depends on device-mapper target registration, `dm_get_device()`/`dm_put_device()`, block bio APIs, zoned block helpers, DAX helpers, and IMA status formatting. It advertises integrity, nowait, host-managed zoned, crypto, and atomic-write passthrough features.

## Risks
Sector parsing and overflow checks are the main constructor risk. Ioctl forwarding is deliberately conservative because forwarding partition or device-size-sensitive ioctls through an offset mapping would be unsafe. DAX page-offset translation must include both the target offset and lower-device start sector. Feature flags assume the lower device capabilities are correctly constrained by dm core queue-limit merging.

## Test Signals
Exercise table creation with invalid counts, invalid offsets, very large offsets, full-device and offset mappings, bio read/write remapping, flush/discard/write-zeroes/secure-erase passthrough, ioctl forwarding refusal on partial maps, zoned report translation, DAX enabled/disabled builds, IMA/table status output, and target register/unregister paths.
