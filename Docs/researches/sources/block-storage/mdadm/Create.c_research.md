# File Research: sources/block-storage/mdadm/Create.c

## Purpose
`Create.c` implements mdadm array creation: validating requested geometry, checking member devices, initializing metadata, adding member disks, optionally zeroing data ranges, and starting or preparing the new array.

## Major Entry Points
- `Create()` is the top-level create-mode implementation.
- `default_layout()` resolves default RAID layouts, preferring metadata-handler defaults when available.
- `add_disks()` performs the two-pass process of adding devices to metadata and then to the kernel array.
- `add_disk_to_super()` assigns disk roles/state and invokes the metadata handler’s `add_to_super()`.
- `update_metadata()` writes initialized metadata, configures internal bitmaps, flushes metadata updates, and updates map entries when external metadata changes UUIDs.
- `write_zeroes_fork()` and `wait_for_zero_forks()` implement optional asynchronous zeroing of data areas.

## Core Control Flow
`Create()` validates required parameters first: RAID level, device counts, RAID6 limits, spare support, bitmap support, and metadata/container constraints. If a single listed device is an md container, it can load container metadata and create a member array inside it.

Defaults are resolved for layout, chunk size, size, and metadata type. Geometry validation is delegated to the selected metadata handler through `validate_geometry()`, including consistency policy and data offset considerations. The code rounds sizes to chunk boundaries where necessary and uses the smallest suitable component size when no explicit size is given.

For each real component device, creation verifies block-device status, determines or parses data offset, validates geometry against the device, accumulates min/max usable sizes, adds drive policy information, and warns about existing ext2, reiserfs, RAID metadata, and partitions. It also warns for boot-related metadata placement and platform compatibility issues.

Before writing anything, warnings require interactive confirmation unless `--run` is used. The code also inserts intentional missing slots for certain RAID4/5/6 creation cases to prefer reconstruction behavior or satisfy kernel start requirements.

The md device is created under a map lock, checked for naming conflicts, initialized with array geometry, and passed to the metadata handler’s `init_super()`. The map is updated before disk addition so udev and other mdadm processes can identify the array.

`add_disks()` blocks SIGINT/SIGCHLD, then runs two passes. Pass one prepares per-disk metadata, removes partitions from opened devices, calls `add_to_super()`, and starts optional zeroing children. After zeroing completes, `update_metadata()` writes initial superblocks and bitmap state. Pass two adds each disk to the kernel md device with `ADD_NEW_DISK`.

After all disks are added, containers are prepared without starting data IO. Non-container arrays are started when `--run` is set or enough devices were supplied. External metadata arrays use sysfs `array_state` and mdmon coordination; native arrays use `RUN_ARRAY` unless readonly sysfs start is requested.

## Dependencies and Integration Points
The file integrates mdadm configuration defaults, metadata supertype operations, md device creation, map locking, udev blocking/unblocking, sysfs attributes, mdmon, policy checks, filesystem/partition probes, and kernel md ioctls.

## Safety and Risk Notes
Creation is careful about existing signatures, partition tables, oversized device differences, unsuitable geometry, unsupported bitmaps/PPL, clustered bitmap node counts, and metadata platform compatibility. Optional zeroing is interrupt-aware: the parent waits for zeroing children even after SIGINT so disks are not left busy in the background. Abort paths remove map entries, close fds, unblock udev, and release policy data.
