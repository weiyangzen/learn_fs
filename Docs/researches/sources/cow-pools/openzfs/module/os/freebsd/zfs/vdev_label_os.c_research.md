# File Research: sources/cow-pools/openzfs/module/os/freebsd/zfs/vdev_label_os.c

## Scope

FreeBSD vdev label OS helpers for writing pad2 boot metadata and checking whether the boot reserve area contains FreeBSD BTX boot code.

## Main Interfaces

- `vdev_label_write_pad2()` writes caller data plus zero padding to the label pad2 area.
- `vdev_check_boot_reserve()` reads the reserved boot area and reports `EBUSY` if BTX magic is present.

## State And Control Flow

`vdev_label_write_pad2()` validates size, leaf status, and liveness; requires full config writer lock; allocates an I/O ABD of `VDEV_PAD_SIZE`; copies input bytes, zero-fills the rest, issues a label write zio at `vl_be`, waits, frees the ABD, and returns the error.

`vdev_check_boot_reserve()` allocates one ashift-sized linear ABD, issues a child read using a negative logical offset to reach `VDEV_BOOT_OFFSET`, waits, inspects the first five bytes for BTX magic, frees the ABD, and returns `EBUSY` or success.

## Dependencies

Uses SPA/vdev label layout constants, ZIO root/child I/O, ABD allocation/copy/zero, and FreeBSD boot-area knowledge.

## Correctness Notes

The boot reserve check protects FreeBSD `zfsboot` data from being overwritten when attaching disks to RAIDZ. `zio_vdev_child_io()` normally offsets by `VDEV_LABEL_START_SIZE`, so this file intentionally passes an offset adjusted below zero to address the reserved area.
