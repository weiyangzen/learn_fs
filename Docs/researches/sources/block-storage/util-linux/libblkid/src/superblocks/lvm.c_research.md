# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/lvm.c

Detector collection for LVM1, LVM2 PVs, DM snapshot COW, DM-verity hash devices, and DM-integrity. LVM2 reads around 0 or 1 KiB, locates the `LABELONE` header, verifies the recorded sector, checks the LVM CRC over the label payload, formats the 32-character PV UUID with LVM dashes, sets version from the label type, and marks the first 8 KiB as a wiper region.

LVM1 verifies version 1 or 2 and formats its PV UUID. DM snapshot COW is magic-only. DM-verity validates version 1 and emits UUID/version. DM-integrity validates nonzero version and emits version.

This file is important for conflict resolution because LVM’s wiper hint tells safe probing that stale partition-table signatures inside the wiped start area should be ignored after an LVM match.
