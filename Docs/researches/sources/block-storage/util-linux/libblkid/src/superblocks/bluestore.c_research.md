# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/bluestore.c

Ceph BlueStore backing block-device detector. It matches the literal `bluestore block device` magic string and reads the small physical header structure through the generic superblock helper.

The custom probe only verifies the buffer can be read; all actual identity comes from the magic table. It reports name `ceph_bluestore` with `BLKID_USAGE_OTHER` and does not expose UUID, label, version, or geometry.
