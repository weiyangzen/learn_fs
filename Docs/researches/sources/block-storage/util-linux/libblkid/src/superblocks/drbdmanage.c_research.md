# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/drbdmanage.c

DRBDmanage control-volume detector. It matches `$DRBDmgr=q` at offset zero, reads the fixed header, verifies the 32-byte UUID field is all hex digits and followed by newline, and stores it as the UUID.

It then reads a persistence header at 0x1000. If the binary persistence magic is present, it emits the version from the version field. The detector reports `drbdmanage_control_volume` with `BLKID_USAGE_OTHER` and a 64 KiB minimum size.
