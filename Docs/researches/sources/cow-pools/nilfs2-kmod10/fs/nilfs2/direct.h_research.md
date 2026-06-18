# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/direct.h

Header for direct bmap implementation. It defines direct block count and key bounds based on inode bmap storage size, and declares initialization plus delete-and-convert support.

Integration: included by generic bmap and direct implementation. The direct key maximum defines the small-map range used by bmap conversion logic.

Risk/notes: direct capacity is tied to `NILFS_BMAP_SIZE` and on-disk inode layout.
