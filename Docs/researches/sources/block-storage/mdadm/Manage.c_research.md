# File Research: sources/block-storage/mdadm/Manage.c

## Purpose
`Manage.c` implements mdadm's runtime management operations for active md arrays: run, stop, read-only/read-write switching, hot add, re-add, remove, fail, replace, preferred replacement, subarray update, spare migration, and kernel autodetect.

## Main Flow
Top-level management enters through `Manage_subdevs()`. It reads array/sysfs metadata, identifies the array supertype, walks the requested component list, expands special operands like `failed`, `detached`, `missing`, and `set-X`, resolves devices to major/minor or sysfs member attributes, and dispatches by disposition character.

`Manage_add()` handles new members, spares, journals, and re-adds. It validates size and metadata, attempts fast re-add through existing superblocks, writes or updates superblocks when needed, freezes the array around risky operations, and finally uses either `ADD_NEW_DISK` or external metadata `sysfs_add_disk()`.

`Manage_remove()`, `Manage_replace()`, and `Manage_with()` implement hot removal, `want_replacement`, and preferred replacement slot assignment through ioctl/sysfs paths.

## Key Behavior
- `Manage_ro()` supports native arrays through `STOP_ARRAY_RO`/`RESTART_ARRAY_RW` and external subarrays by editing `metadata_version`, changing `array_state`, and pinging mdmon.
- `Manage_stop()` obtains exclusive access, handles mdmon-managed subarrays/containers, blocks container stop while member subarrays are active, tries to pause reshapes at a reversible stripe boundary, retries transient `EBUSY`, removes mdadm-created device links, and updates the map file.
- Re-add logic compares member UUIDs and slot state, optionally updates write-mostly/failfast/superblock fields, and handles clustered add/candidate flags.
- External metadata add paths validate geometry/policies, kill old metadata, add to the metadata handler, sync or notify mdmon, and add the device through sysfs.
- Journal add requires the array to be read-only and switches it back to writable after successful hot add.
- Faulting a device is guarded by `is_remove_safe()`, which ensures the remaining synced slots satisfy md redundancy rules.
- Clustered md uses special states for candidate/cluster add and `CLUSTERED_DISK_NACK` for failed cluster confirmation.
- `Update_subarray()` opens a container subarray, validates active-state restrictions, applies metadata-specific updates, and flushes mdmon metadata updates when needed.
- `move_spare()` removes a spare from one array and adds it to another, rolling back on destination failure.

## Integration Notes
The file depends heavily on mdadm core helpers, sysfs md attributes, md ioctls, metadata supertype methods, mdmon monitor/manager signaling, map-file locking, udev availability, policy checks, and kernel md state names.

## Risks
The file coordinates live kernel state, raw component devices, metadata handlers, and mdmon, so races are central. Sensitive areas include exclusive-open retry windows, reshape freeze/unfreeze behavior, external container holder checks, cleanup after partially written superblocks, clustered flags, and preserving user-visible return codes for test mode and busy devices.
