# File Research: sources/block-storage/linux-dm/drivers/md/md-linear.c

## Purpose
Implements the deprecated MD `linear` personality, concatenating component devices into a single logical address space.

## Main Interfaces
- Mapping: `which_dev()`, `linear_make_request()`.
- Configuration: `linear_conf()`, `linear_run()`, `linear_add()`, `linear_free()`.
- Size/status: `linear_size()`, `linear_status()`, `linear_quiesce()`.
- Registered personality: `linear_personality`.

## Control Flow
`linear_conf()` builds a `linear_conf` with one `dev_info` per raid disk, validates raid-disk numbering, optionally rounds rdev sizes down to `chunk_sectors`, stacks queue limits, records discard support, computes cumulative end sectors, and stores a stable copy of `raid_disks`.

`linear_make_request()` handles flushes through MD flush logic, binary-searches the component containing the bio sector, validates bounds and broken-device state, splits bios that cross component boundaries, remaps the bio sector to the component’s `data_offset`, ignores discards on devices without discard support, traces the remap, applies write-same/write-zeroes checks, and submits the bio to the component.

`linear_add()` supports growing the array by replacing the private configuration with a newly allocated one under MD suspend/resume, incrementing `raid_disks`, updating capacity, and freeing the old config with RCU.

## State And Synchronization
`mddev->private` points to `linear_conf`. Config replacement uses `rcu_assign_pointer()` and `kfree_rcu()` because old readers can still walk the old disk array. Array-wide changes are bracketed by `mddev_suspend()` and `mddev_resume()`.

## Integration Points
Uses MD core personality registration, no-bitmap validation, disk limit stacking, integrity registration, flush handling, capacity updates, block remap tracing, and write-same/write-zeroes checks.

## Notable Behaviors
- Logical mapping is cumulative and found via binary search over `end_sector`.
- Any component supporting discard enables discard at the MD queue; per-bio discard is silently completed if the chosen component lacks discard.
- Hot-add requires the new rdev’s saved raid disk to equal the current number of raid disks.
- The status output reports chunk-sector rounding in KiB.

## Risks And Review Focus
- Boundary splitting must ensure the original remainder is submitted after the split bio and with correct chaining.
- Discard support is coarse at queue level but per-device at submission, which can make discard behavior uneven.
- Config replacement relies on all readers honoring RCU lifetime assumptions.
