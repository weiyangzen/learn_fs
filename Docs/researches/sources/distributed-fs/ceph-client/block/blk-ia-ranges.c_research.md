# sources/distributed-fs/ceph-client/block/blk-ia-ranges.c

## Purpose
`blk-ia-ranges.c` manages independent access ranges for block devices. These ranges describe non-overlapping, capacity-covering LBA regions that can be accessed independently, and it exposes them through queue sysfs under `independent_access_ranges`.

## Important APIs, Types, and Functions
Public functions are `disk_alloc_independent_access_ranges()` and `disk_set_independent_access_ranges()`. Queue registration paths use `disk_register_independent_access_ranges()` and `disk_unregister_independent_access_ranges()`. Static helpers include sysfs show methods for `sector` and `nr_sectors`, `disk_find_ia_range()`, `disk_check_ia_ranges()`, and `disk_ia_ranges_changed()`.

## Control Flow
Drivers allocate a `struct blk_independent_access_ranges` sized for `nr_ia_ranges`, fill each range, and call `disk_set_independent_access_ranges()`. That function takes `q->sysfs_lock`, validates the proposed ranges, frees unchanged replacements, unregisters the old set, assigns the new set, and registers sysfs immediately if the queue is already registered.

Validation requires at least one range, no overlap, no holes, sorted coverage from sector zero, and total coverage equal to disk capacity. It sorts in place by repeatedly finding the range that starts at the expected sector and swapping it into position. Sysfs registration creates a parent `independent_access_ranges` kobject and numbered child kobjects, each exposing read-only `sector` and `nr_sectors`.

## State and Persistence
Runtime state hangs off `disk->ia_ranges`. Sysfs registration state is tracked by `iars->sysfs_registered` and kobjects embedded in the parent and each range. Range memory is freed only after kobject teardown is safe; individual range kobject release is intentionally a no-op because the parent allocation owns the flexible array.

## Dependencies and Integration Points
The file depends on `gendisk`, request queue sysfs locking, queue registration state, disk capacity, and kobject sysfs. It is driver-facing through exported allocation/set APIs and user-facing through queue sysfs.

## Risks
Risks include invalid device topology exposure, kobject lifetime mistakes, leaks on partial sysfs registration failure, and racing revalidation with queue sysfs. The validation rejects holes and capacity mismatch to prevent user space from relying on incomplete topology. Lockdep assertions enforce `q->sysfs_lock` for register/unregister.

## Test Signals
Tests should cover unsorted valid ranges, overlaps, holes, capacity mismatch, zero ranges, unchanged replacement freeing, setting NULL to clear, register/unregister before and after queue registration, partial child kobject failure unwinding, and sysfs values for each numbered range.
