# File Research: sources/block-storage/mdadm/Assemble.c

## Purpose
`Assemble.c` implements mdadm array assembly: discovering member devices, matching metadata identity, merging with partially assembled arrays, updating superblocks when requested, adding disks to the kernel md device, and starting arrays or container subarrays.

## Major Entry Points
- `Assemble()` is the top-level implementation for assembling a native md array or dispatching container member assembly.
- `assemble_container_content()` assembles and activates a member array described by external/container metadata.
- `select_devices()` scans candidate devices, loads metadata, applies identity matching, handles containers, and marks candidate devices for use.
- `load_devices()` rereads selected devices, optionally updates metadata, records disk roles/events, and builds the best-device table.
- `force_array()` implements `--force` event-count promotion for degraded arrays when enough safe devices are not otherwise available.
- `start_array()` sets kernel array metadata, adds selected disks, and starts or leaves the array assembled depending on policy.

## Core Control Flow
Assembly begins by requiring either explicit devices or enough identity information such as UUID, name, super-minor, member/container, or configured device filters. If metadata type was specified, it resolves a matching supertype. Without an explicit device list it uses configured devices from mdadm configuration.

`select_devices()` walks candidates and rejects devices that fail block-device checks, cannot be opened, do not contain recognizable metadata, conflict with explicit `devices=` or `container=`, are disabled by auto-assembly metadata policy, have mismatched UUID/name/level/raid-disk count, or are already assembled. Containers are handled specially: the code loads container metadata, scans contained member arrays, rejects busy or blocked members, and returns the matching member content rather than ordinary disk content.

After selection, `Assemble()` locks the mdadm map file and checks whether the array UUID already has a partially assembled md device. If so, it merges pre-existing sysfs devices into the device list and opens that md device. Otherwise it chooses a trusted name based on homehost, configuration, metadata, and command-line context, then creates a new md device.

For native arrays, `load_devices()` rereads metadata under exclusive open where needed, applies requested `--update` operations, stores updated superblocks, identifies the most recent active member by event count, and maps roles to best slots. It also detects suspicious duplicate 0.90 superblocks that may indicate overlapping partitions.

The main assembly logic counts up-to-date active devices, spares, journal devices, and rebuilding devices. Event counters must be current or within the kernel-compatible margin; devices reporting the most recent device as failed are ignored unless forced. With `--force`, `force_array()` can rewrite selected stale superblocks to the most recent event count, with reshape-progress safeguards.

Before start, the code reloads the chosen superblock, initializes sysfs, normalizes desired device states, optionally marks a forced dirty array clean, handles lockless bitmap setup, restores reshape backup data through grow helpers, updates the map, then calls `start_array()`.

## Container/Subarray Behavior
`assemble_container_content()` initializes sysfs for the member, removes old devices no longer in metadata, adds new and expansion devices, updates the map, validates or rewrites PPL when supported, checks `enough()` availability, blocks unsafe dirty degraded RAID4/5/6 unless policy allows it, configures internal bitmaps, handles reshape backup/continuation, starts mdmon for external metadata, sets array state through sysfs, and emits assembly status.

## Dependencies and Integration Points
This file depends heavily on mdadm shared APIs from `mdadm.h`: supertype operations, map locking/updating, sysfs helpers, mdstat parsing, policy/domain checks, md ioctls, mdmon control, grow/reshape helpers, and disk add/remove helpers. It bridges userspace metadata handlers with kernel md activation via `SET_ARRAY_INFO`, `ADD_NEW_DISK`, `RUN_ARRAY`, sysfs `array_state`, and related attributes.

## Safety and Risk Notes
Assembly is intentionally conservative around metadata mismatches, active arrays, busy members, event-count divergence, reshape progress disagreement, missing/stale journals, invalid PPL, and dirty degraded RAID4/5/6. `--force` can rewrite superblocks and mark arrays clean, and the code prints explicit warnings where that may risk corruption. The map lock is central to avoiding races with incremental assembly and udev/mdadm monitor behavior.
