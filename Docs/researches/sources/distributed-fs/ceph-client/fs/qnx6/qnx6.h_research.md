# sources/distributed-fs/ceph-client/fs/qnx6/qnx6.h

## Purpose
`qnx6.h` defines private QNX6 filesystem state, endian-aware on-disk integer helpers, mount option helpers, and cross-file declarations.

## Important APIs, types, and functions
It defines `__fs16`, `__fs32`, `__fs64`, `struct qnx6_sb_info`, `struct qnx6_inode_info`, accessors `QNX6_SB`/`QNX6_I`, mount-option macros, and conversion helpers `fs16_to_cpu`, `fs32_to_cpu`, `fs64_to_cpu`, plus CPU-to-filesystem variants.

## Control flow
Runtime endianness stored in `s_bytesex` controls every on-disk integer conversion, allowing the same code to read little- and big-endian images.

## State and persistence
The header defines runtime superblock and inode-private state but does not mutate storage.

## Dependencies and integration points
It depends on VFS/pagemap types and `linux/qnx6_fs.h`, and is shared by QNX6 inode, dir, namei, and MMI superblock code.

## Risks and test signals
Risks include missing endian conversions at call sites, mount option bit misuse, and private inode lifetime issues. Test signals include endian-swapped filesystem images, MMI option display, direct/indirect pointer conversions, and compile coverage with debug enabled.
