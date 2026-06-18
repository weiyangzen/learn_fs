# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/ext.c

ext-family detector for JBD, ext2, ext3, ext4, and ext4dev. It reads the ext superblock at 1024 bytes, validates metadata checksums when the metadata-csum feature is set, and retries with O_DIRECT after a checksum failure to avoid races with concurrent superblock writes. Legacy filesystems without checksums get an additional block-size sanity check.

The shared `ext_get_info` path emits label, filesystem UUID, journal UUID when present, optional `SEC_TYPE=ext2`, version, block size, last block, and filesystem size. Individual probes distinguish JBD journal devices, ext2 without journal/unsupported features, ext3 with journal but without ext4-only features, ext4 with ext4-only features, and ext4dev test filesystems.

The file’s correctness depends on feature-bit classification and conservative unsupported-feature masks. FSSIZE intentionally uses raw block count and does not subtract ext metadata/journal overhead.
