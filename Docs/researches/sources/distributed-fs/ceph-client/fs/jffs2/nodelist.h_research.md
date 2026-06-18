# sources/distributed-fs/ceph-client/fs/jffs2/nodelist.h

## Purpose
`nodelist.h` defines the central JFFS2 in-core data structures, endian conversion helpers, node/ref flags, allocation constants, fragment-tree helpers, and cross-file function prototypes. It is the shared contract for scan, readinode, write, GC, erase, compression, xattr, and debug subsystems.

## Important APIs, Types, And Functions
Important types include `jffs2_raw_node_ref`, `jffs2_inode_cache`, `jffs2_full_dnode`, `jffs2_tmp_dnode_info`, `jffs2_readinode_info`, `jffs2_full_dirent`, `jffs2_node_frag`, and `jffs2_eraseblock`. Important macros include endian wrappers, `REF_UNCHECKED`, `REF_OBSOLETE`, `REF_PRISTINE`, `REF_NORMAL`, `ref_flags()`, `ref_offset()`, `dirent_node_state()`, `ALLOC_*`, `VERYDIRTY()`, `ISDIRTY()`, and `PAD()`. Inline helpers cover ref traversal, inode-cache recovery from raw refs, device encoding, and rbtree navigation.

## Control Flow
The header's prototypes define major subsystem boundaries: node-list mutation, node management reservations, writes, readinode, allocation, GC, read, scan, build, erase, and write-buffer operations. Raw-node refs chain physically through eraseblocks and logically through inode/xattr caches; fragment rbtrees map current file ranges to full dnodes or holes.

## State And Persistence Behavior
These structures are volatile reconstructions of persistent raw flash nodes. Ref flags encode whether on-flash nodes are unchecked, obsolete, pristine, or normal. Eraseblock accounting fields drive GC and allocation decisions; inode-cache state controls mount checking, read-inode races, GC exclusion, and deletion lifetime.

## Dependencies And Integration Points
The header includes OS abstraction (`os-linux.h` or `os-ecos.h`), superblock/inode private headers, xattr, ACL, summary, Linux VFS, rbtrees, and JFFS2 raw format definitions. It is included by nearly all files in this subset.

## Risks And Test Signals
Because this header defines shared invariants, small changes can break many subsystems. Risks include endian conversion mismatch, ref flag misuse in low flash-offset bits, inode-cache terminal-pointer assumptions, rbtree macro misuse on NULL, and eraseblock accounting drift. Tests should include cross-endian image compatibility, mount scan/read/write/GC cycles, xattr-enabled builds, NAND write-buffer builds, raw-node ref traversal over chained blocks, and debug sanity/paranoia configurations.
