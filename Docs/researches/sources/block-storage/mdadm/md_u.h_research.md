# File Research: sources/block-storage/mdadm/md_u.h

## Role

`md_u.h` defines the ioctl interface and userspace structures for communication between mdadm and the Linux md kernel driver. It is the operational ABI counterpart to `md_p.h`’s on-disk format definitions.

## Ioctl Definitions

Status ioctls:

- `RAID_VERSION`
- `GET_ARRAY_INFO`
- `GET_DISK_INFO`
- `RAID_AUTORUN`
- `GET_BITMAP_FILE`

Configuration ioctls:

- `ADD_NEW_DISK`
- `HOT_REMOVE_DISK`
- `SET_ARRAY_INFO`
- `SET_DISK_FAULTY`
- `SET_BITMAP_FILE`

Usage/lifecycle ioctls:

- `RUN_ARRAY`
- `STOP_ARRAY`
- `STOP_ARRAY_RO`
- `RESTART_ARRAY_RW`
- `CLUSTERED_DISK_NACK`

## Structures

- `mdu_version_t` reports kernel md version.
- `mdu_array_info_t` carries array identity, version, creation time, level, size, disk counts, preferred minor, persistence flag, state counters, layout, and chunk size.
- `mdu_disk_info_t` carries one disk’s number, major/minor, role, and state.
- `mdu_start_info_t` carries disk start info.
- `mdu_bitmap_file_t` contains a bitmap pathname buffer.
- `mdu_param_t` carries run parameters: personality, chunk size, and unused max fault.

## Dependencies

The ioctl numbers use `MD_MAJOR` and `_IO*` macros from system/kernel headers included through mdadm’s common headers. The structures are consumed throughout mdadm’s manage/build/create/assemble paths.

## Important Invariants

- Structure layouts are ABI contracts with the kernel.
- Field widths are plain `int`/`unsigned int`, reflecting historical ioctl ABI rather than modern extensible netlink-like design.
- `mdu_array_info_t` overlaps concepts from the physical superblock but represents runtime kernel state.

## Risks

These ioctls are legacy but still central. Changing structure definitions or ioctl constants would break kernel compatibility. New code should prefer sysfs where mdadm already does, but these definitions remain necessary for existing operations.
