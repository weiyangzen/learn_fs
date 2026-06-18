# File Research: sources/block-storage/parted/libparted/fs/amiga/apfs.c

Probe implementation for Amiga `apfs1` and `apfs2` types, corresponding to PFS-style signatures `0x50463101` and `0x50463102`. `_generic_apfs_probe()` reads the boot block, checks the signature, then reads a root block at `geom->start + reserved * blocksize` and validates that it has the same kind value.

Like the AFFS probe, it only works on 512-byte sector devices and optionally uses `amiga_find_part()` to derive reserved blocks and filesystem block size from the matching RDB partition block. It returns a duplicate of the input geometry on success and `NULL` on mismatch or read/allocation failure.

The probe is intentionally shallow: root validation is just a kind comparison. It does not checksum APFS/PFS metadata or calculate a more precise filesystem length.
