# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/befs.c

BeFS detector with substantial metadata traversal. It recognizes little- and big-endian BeFS superblocks at primary and alternate offsets, validates all three superblock magic fields, confirms block size/shift consistency, and avoids undefined shifts by checking allocation-group plus block-shift bounds.

Beyond the superblock, it attempts to recover the BeFS volume UUID from the root inode’s small data area or from the attribute B+tree. Helpers translate BeFS block runs through direct, indirect, and double-indirect data streams, compare B+tree keys, and follow bounded B+tree loops to find `be:volume_id`.

On success it emits label, endian-specific version string, formatted 64-bit UUID when found, filesystem/device block size, and endianness. The file’s complexity is in defensive parsing of BeFS inode and B+tree metadata; malformed structures generally return no match rather than crashing or trusting the initial magic.
