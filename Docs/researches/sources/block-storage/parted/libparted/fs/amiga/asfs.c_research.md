# File Research: sources/block-storage/parted/libparted/fs/amiga/asfs.c

ASFS filesystem probe implementation. `_asfs_probe()` requires 512-byte sectors, optionally reads the Amiga RDB partition block to get filesystem block size, then validates ASFS root blocks.

The ASFS root signature is `0x53465300`. `_asfs_probe_root()` checks the signature, verifies a big-endian checksum with initial sum `1`, checks that the root block number encoded in the block maps to the root sector being tested, and verifies 64-bit start/end byte ranges match the input geometry. The probe checks the first root at partition start and a second root near the end, accepting the filesystem if either validates.

The implementation returns a duplicate of the input geometry on detection. It does not attempt repair or detailed metadata parsing, but its start/end checks make it stricter than the APFS/PFS probe.
