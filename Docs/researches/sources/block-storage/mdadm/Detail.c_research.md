# File Research: sources/block-storage/mdadm/Detail.c

## Purpose
`Detail.c` implements mdadm detail/reporting commands for active md arrays, inactive arrays, containers, subarrays, platform metadata support, and export/brief output modes.

## Major Entry Points
- `Detail(char *dev, struct context *c)` prints or exports array details for one md device.
- `Detail_Platform(struct superswitch *ss, int scan, int verbose, int export, char *controller_path)` reports metadata platform support.
- `detail_fname_from_uuid()` formats UUIDs for detail output with special super1 byte-order handling.

## Core Control Flow
`Detail()` opens the md device, reads sysfs metadata and device state when available, falls back to `GET_ARRAY_INFO`, and resolves external metadata/container status. If the device is a subarray, it identifies the parent container and member name, then loads container content.

To obtain richer metadata, it scans active member devices from sysfs or ioctl disk info, opens component devices, loads superblocks through the selected supertype, and extracts mdinfo. It avoids using free-floating spares with zero UUID as the authoritative source.

In `--export` mode, it emits shell-style key/value records such as `MD_LEVEL`, `MD_DEVICES`, `MD_CONTAINER`, `MD_MEMBER`, `MD_METADATA`, `MD_UUID`, `MD_DEVNAME`, reshape status, metadata-specific exported detail, and per-device role/path records unless device output is suppressed.

In brief mode, it prints an `ARRAY` or `INACTIVE-ARRAY` line suitable for configuration-like output, including level, device count, container/member or metadata, bitmap path, spares, metadata-specific brief detail, and optionally sorted device paths.

In full mode, it prints human-readable fields: metadata version, creation/update time, raid level, array and component sizes, device counts, persistence, bitmap information, state/degraded/resync status from `/proc/mdstat`, layout, chunk size, consistency policy, reshape details, metadata-specific detail, member arrays for containers, and a component table.

## Device State Handling
The component table reserves two slots per raid disk so replacements can be displayed next to primary devices, with extra devices after active slots. It reports faulty, active, sync, removed, writemostly, failfast, journal, spare, and rebuilding state. RAID10 near/far layouts may print set letters for synced members.

## Dependencies and Integration Points
This file uses sysfs readers, md ioctls, mdstat parsing, metadata supertype detail callbacks, map lookup helpers, preferred device-name mapping, container/subarray helpers, consistency-policy mappings, bitmap dirtiness checks, and platform-detail callbacks.

## Safety and Risk Notes
`Detail()` is read-oriented, but its return value changes in test mode: it indicates failed or insufficient arrays through `rv`. Export output depends on map file availability for UUID/devname records. The code contains a likely typo in `if (fstat(fd, &stb) != 0 && !S_ISBLK(stb.st_mode))`, where `stb` is consulted after failed `fstat`; the intended condition was probably failure or non-block device.
