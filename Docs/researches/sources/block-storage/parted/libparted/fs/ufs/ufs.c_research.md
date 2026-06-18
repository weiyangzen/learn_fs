# File Research: sources/block-storage/parted/libparted/fs/ufs/ufs.c

Purpose: Detection-only UFS backend for Sun and HP UFS variants.

Main interfaces: Registers two filesystem types, `sun-ufs` and `hp-ufs`, each with a probe operation.

Control flow: Both probes read the UFS superblock area around offset 16 * 512 bytes. `ufs_probe_sun()` accepts the standard UFS magic in either big-endian or little-endian form. `ufs_probe_hp()` accepts HP magic variants `UFS_MAGIC_LFN`, `UFS_MAGIC_FEA`, and `UFS_MAGIC_4GB`, again in either endian form. Successful probes compute returned geometry from `fs_bsize / sector_size * fs_size`.

Dependencies: The file embeds a packed UFS superblock layout adapted from Linux `ufs_fs.h`, uses libparted geometry/endian/debug APIs, and registers file system types with libparted.

Important details and risks: The struct-size assertion guards layout drift. Detection is magic-and-size based and does not verify secondary consistency. Reads assume the superblock spans three 512-byte sectors rounded to the device sector size. Tests should cover endian variants, HP-specific magics, devices shorter than five sectors, and unusual sector sizes.
