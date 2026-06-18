# sources/distributed-fs/ceph-client/include/uapi/linux/jffs2.h

## Purpose
`jffs2.h` defines JFFS2 flash filesystem on-media constants, node formats, compression identifiers, feature compatibility bits, summary structures, xattr records, and device-node encodings.

## Important APIs, Types, and Functions
It exports magic values, maximum name length, compression IDs, feature masks, node type constants, xattr prefixes, inode flags, endian-aware integer typedef wrappers, and raw node structures: `jffs2_unknown_node`, `jffs2_raw_dirent`, `jffs2_raw_inode`, `jffs2_raw_xattr`, `jffs2_raw_xref`, `jffs2_raw_summary`, `jffs2_node_union`, and `jffs2_device_node`.

## Control Flow
Mount or image-scan code walks flash eraseblocks, validates node magic/type/crc, interprets compatibility bits, reconstructs inode and directory state from append-only nodes, applies compression, and uses summaries to accelerate scanning.

## State and Persistence
All defined structures are persistent flash metadata. Runtime state such as inode caches, eraseblock lists, and garbage-collection decisions is built from these records by the filesystem driver.

## Dependencies and Integration Points
It includes `<linux/types.h>` and `<linux/magic.h>`. Integration points include the JFFS2 filesystem, MTD devices, image creation tools, flash recovery tooling, compression backends, xattr/ACL handling, and device special files.

## Risks and Test Signals
Tests should cover endian handling, CRC validation, unknown feature compatibility behavior, summary node parsing, xattr/xref consistency, compression ID handling, and malformed variable-length name/data fields. Layout changes would directly affect on-flash compatibility.
