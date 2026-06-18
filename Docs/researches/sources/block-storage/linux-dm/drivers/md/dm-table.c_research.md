# File Research: sources/block-storage/linux-dm/drivers/md/dm-table.c

## Purpose
Implements DM table creation, target loading, device acquisition, target lookup indexing, table type selection, queue-limit calculation, integrity/crypto propagation, and target suspend/resume dispatch.

## Main Responsibilities
- Allocate/destroy `struct dm_table`.
- Add target lines and call target constructors.
- Manage underlying devices used by targets.
- Build a btree-like index over target end sectors for fast bio lookup.
- Decide whether a table is bio-based, DAX bio-based, or request-based.
- Calculate stacked queue limits and feature flags.
- Register/verify integrity and inline crypto profiles.
- Dispatch target lifecycle hooks for suspend/resume.

## Control Flow
- `dm_table_create()` allocates a table, initializes the devices list, rounds target capacity to index-node size, and allocates target/high arrays.
- `dm_table_add_target()` validates table continuity, target singleton/immutable/writeability constraints, resolves target type, splits target arguments, calls `ctr`, and appends the target high sector.
- `dm_split_args()` destructively tokenizes constructor/message strings with backslash quoting.
- `dm_table_complete()` determines queue mode, builds the index, registers integrity, constructs inline crypto profile, and allocates mapped-device mempools.
- `dm_table_find_target()` uses the generated index to map a sector to the target covering it.
- `dm_calculate_queue_limits()` stacks limits from each target’s devices, validates mapped device areas, handles zoned constraints, and checks logical block alignment.
- `dm_table_set_restrictions()` applies final queue flags and limits to the mapped-device queue.
- `dm_table_resume_targets()` runs all `preresume` hooks first, aborting on failure, then runs all `resume` hooks.

## Device Management
- `dm_get_device()` accepts major:minor strings or paths, reuses existing table devices, upgrades open mode when necessary, and reference-counts each `dm_dev_internal`.
- `dm_put_device()` decrements table-device references and releases devices when the count reaches zero.
- `free_devices()` warns and cleans up any leaked target device references during table destruction.

## Queue Type Rules
- Mixed bio-based and request-based targets are rejected.
- Hybrid targets inherit the live device type when possible, otherwise default to bio-based.
- DAX bio-based mode is selected only if all targets/devices support DAX or there are no devices and the live table is already DAX bio-based.
- Request-based tables must have a single immutable target, no target-level I/O splitting, and request-stackable underlying whole devices.

## Queue Limits and Feature Propagation
- Stacks physical/logical block sizes, alignment, discard, zone, and related limits.
- Validates zoned model consistency and zone size compatibility.
- Enables or disables:
  - nowait
  - discard
  - secure erase
  - write cache/FUA
  - DAX and synchronous DAX
  - nonrotational
  - write same
  - write zeroes
  - stable writes
  - add_random
- Runs zoned queue restriction setup when the resulting queue is zoned.

## Integrity and Inline Crypto
- Integrity is registered when all targets pass integrity and all devices expose matching profiles, unless a target handles integrity itself.
- On resume, integrity is reverified and unregistered if profiles no longer match.
- With `CONFIG_BLK_INLINE_ENCRYPTION`, a DM crypto profile is built as the intersection of underlying capabilities and cannot remove capabilities already exposed by the mapped-device queue.

## Dependencies
- DM core mapped-device APIs.
- Target-type registry from `dm-target.c`.
- Block queue limit, integrity, crypto, DAX, blk-mq, and zoned APIs.
- Device lookup/open helpers.

## Risk and Test Focus
- Table-line continuity and constructor failure cleanup are critical for safe table load rejection.
- Device mode upgrade must not expose partially reopened devices.
- Queue-limit stacking for mixed devices, zoned devices, and target `io_hints` is high risk.
- Request-based table acceptance has strict invariants; regressions can break block-layer assumptions.
- Inline crypto profile updates intentionally disallow capability removal.
