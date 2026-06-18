# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/gfs.c

GFS and GFS2 detector. Both formats share the same magic at 64 KiB, then diverge by filesystem and multihost format ranges. GFS1 requires exact legacy format constants, while GFS2 accepts format ranges 1800-1899 and 1900-1999.

Both probes emit the lock table as label when present and the superblock UUID. GFS2 also emits version `1` and block size. The idinfos set a 32 MiB minimum size reflecting the minimal GFS journal size.
