# File Research: sources/block-storage/parted/libparted/labels/dvh.h

This header defines the on-disk SGI Disk Volume Header structures and constants consumed by `dvh.c`.

Key definitions:
- `struct device_parameters`: SGI/IRIX device geometry and controller parameters.
- `struct volume_directory`: named volume-header file entries with logical block and byte length.
- `struct partition_table`: SGI logical partition entries with first LBN, block count, and partition type.
- `struct volume_header`: 512-byte sector-0 SGI volume header containing magic, root/swap indices, boot filename, device parameters, volume directory, partition table, checksum, and fill.
- Partition type constants include `PTYPE_VOLHDR`, replacement areas, raw, BSD, SysV, EFS, volume, XFS, XFS log, XLV, XVM, and ARCS FAT/extended values.
- Defines `VHMAGIC`, `NPARTAB == 16`, `NVDIR == 15`, `VDNAMESIZE == 8`, and `BFNAMESIZE == 16`.

Behavioral context:
- Comments document the checksum rule: zero `vh_csum`, sum the full structure, store the 32-bit two’s-complement so validation sums to zero.
- Notes that the volume header is sector 0 and historically had unused sector-0 copies on each track of cylinder 0.

Risk notes:
- The header is a raw disk format contract; layout, endian conversion, and struct size assumptions are critical.
- `BOOTABLE` and `NOT_BOOTABLE` macros include trailing semicolons, but they are not used by the listed implementation.
