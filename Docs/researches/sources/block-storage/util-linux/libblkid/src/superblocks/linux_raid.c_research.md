# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/linux_raid.c

Linux MD RAID detector for legacy 0.90-style and version 1.x superblocks. The 0.90 path reads the reserved end-of-device area, accepts little- or big-endian magic, reconstructs the set UUID, validates that the component size fits before the superblock, and avoids whole-disk false positives when the superblock is covered by an existing partition table.

The 1.x path reads superblocks at v1.0, v1.1, and v1.2 locations, validates magic, major version, recorded superblock sector offset, and checksum over the variable `dev_roles` array. It emits set UUID, device UUID as `UUID_SUB`, and set name.

The top-level probe tries v0.90, v1.0, v1.1, and v1.2 in order, setting version for 1.x matches. Signature magic is recorded for wiping. Risk points are variable checksum length and offset calculations, both guarded by reads through the probe buffer API.
