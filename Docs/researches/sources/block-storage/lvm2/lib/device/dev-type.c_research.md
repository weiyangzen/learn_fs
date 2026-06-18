# File Research: sources/block-storage/lvm2/lib/device/dev-type.c

## Purpose
Implements LVM2 device type recognition, partition detection, topology/sysfs property reads, blkid filesystem probing, and signature wiping dispatch. It is the central implementation behind `dev-type.h`, mapping kernel block major names to LVM behavior and exposing helpers used by filters, PV creation, lvresize filesystem handling, and device identity logic.

## Main Responsibilities
- Defines `dev_known_types[]`, the built-in major-name table with max partition counts for sd, md, loop, device-mapper, dasd, nvme, virtio, zram, and other block drivers.
- Builds `struct dev_types` from `/proc/devices` plus optional `devices/types` config overrides in `create_dev_types`.
- Classifies device subsystems with helpers such as `dev_is_nvme`, `dev_is_scsi`, `dev_is_mpath`, `dev_is_lv`, `dev_subsystem_part_major`, and `dev_subsystem_name`.
- Detects whether a device is partitionable and whether it has an actual partition table, using sysfs, native MBR/GPT reads, DASD CDL checks, and optional udev properties.
- Resolves partition devices to primary devices with `dev_get_primary_dev`, using known major/minor partition math first and sysfs parent lookup as fallback.
- Provides blkid-backed filesystem information via `fs_block_size_and_type` and `fs_get_blkid` when `BLKID_WIPING_SUPPORT` is compiled in.
- Wipes existing signatures with blkid when enabled, otherwise falls back to native LVM checks for MD, swap, and LUKS.
- Reads Linux queue/topology attributes such as alignment offset, minimum/optimal IO size, discard limits, rotational flag, and DAX/pmem status.

## Important Control Flow
`create_dev_types` reads the block-device section of `/proc/devices`, records special majors, flags SCSI-like majors, and sets max partition counts by matching `dev_known_types[]`. Device type config entries can override or supplement built-ins.

Partition detection starts with `_is_partitionable`; it treats DM, MD, NVMe whole devices, and loop devices with `loop/partscan` as partitionable even when normal major/minor math is insufficient. `_has_partition_table` reads sector zero for MSDOS partition entries and GPT PMBR; `_has_gpt_partition_table` then reads GPT header and partition entries, counting only nonzero type GUID entries.

`dev_get_primary_dev` returns `1` when the input is already a whole/primary device and `2` when it identifies a partition's parent. NVMe bypasses major/minor arithmetic because blkext numbering does not encode parent/partition in the same way as classic disk majors.

`wipe_known_signatures` chooses the blkid implementation based on `allocation/use_blkid_wiping` and compile-time support. The blkid path repeatedly probes, prompts or skips based on flags, zeroes reported magic bytes, then steps back to verify wiped signatures.

## Dependencies
Depends on LVM device I/O helpers (`dev_read_bytes`, `dev_write_zeros`, direct block-size reads), devmapper UUID helpers, command context config, sysfs path helpers, optional libblkid, optional libudev, and external signature recognizers declared in `dev-type.h` such as MD, swap, LUKS, and DASD checks.

## Risk Notes
- Partition-table detection reads raw on-disk structures and deliberately ignores GPT PMBR alone; changes must preserve this distinction.
- Sysfs fallback paths rely on Linux `/sys/dev/block/<maj>:<min>` layout and symlink structure.
- Blkid signature wiping can be destructive; prompt/exclusion/no-prompt flags are the safety boundary.
- Topology attributes are returned in sectors after shifting byte values; invalid non-4K multiples are normalized for minimum/optimal IO size.
