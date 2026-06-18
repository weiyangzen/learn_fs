<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/qnx4_fs.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/qnx4_fs.h

Purpose: defines on-disk QNX4 filesystem constants and structures for superblocks, inodes, links, and extent blocks.

Important APIs and types: constants define root inode, block and directory entry sizes, name limits, extent counts, filesystem status, inode status flags, and magic integration. `struct qnx4_inode_entry`, `qnx4_link_info`, `qnx4_xblk`, and `qnx4_super_block` describe the serialized disk layout.

Control flow: the QNX4 filesystem driver reads the superblock and inode entries, follows direct and extended extent blocks, resolves long-name link entries, and maps file data from extents. The header itself is data-layout only.

State and persistence: all structures represent persistent on-disk metadata in little-endian or QNX-specific fixed layouts: inode times, sizes, extents, owner/group/mode, link counts, and superblock root records.

Dependencies and integration points: depends on `linux/qnxtypes.h`, Linux fixed types, and filesystem magic constants. Integrates with the QNX4 filesystem driver, VFS, mount tools, and forensic/recovery utilities.

Risks and test signals: risks include malformed disk images, endian/packing drift, extent chain loops, long filename link resolution bugs, and fixed 512-byte block assumptions. Test mounting valid QNX4 images, fsck/forensic comparisons, corrupted extent blocks, long names, and read-only behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/qnx4_fs.h -->
