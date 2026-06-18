# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/bcache.c

Detector for both legacy bcache backing/cache devices and bcachefs filesystems. The bcache path validates the CRC64 checksum across the active journal-bucket portion of the superblock, checks the recorded offset, emits version, UUID, label, block size, and marks the initial bcache metadata area as a wiper region.

The bcachefs path validates the superblock offset, device index/count, variable superblock size, maximum layout size, and checksum type. It supports none, CRC32C, CRC64, and XXH64 checksums, then emits user UUID, primary label, bcachefs major/minor version, block sizes, total filesystem size, and UUID_SUB for the current member.

It also parses variable bcachefs superblock fields for members v1/v2 and disk groups. That logic bounds every dynamic field against the read superblock, sums member bucket sizes into FSSIZE, and reconstructs hierarchical disk-group labels into `LABEL_SUB`. Risk centers on dynamic field size arithmetic, but the code uses explicit range checks before walking variable data.
