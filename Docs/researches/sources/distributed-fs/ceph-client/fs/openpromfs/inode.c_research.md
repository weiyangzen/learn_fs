## sources/distributed-fs/ceph-client/fs/openpromfs/inode.c

### Purpose
This file implements `openpromfs`, a single-superblock pseudo filesystem exposing OpenPROM device-tree nodes as directories and firmware properties as regular files, usually under `/proc/openprom` or equivalent mounts.

### Important APIs, types, and functions
- `struct op_inode_info` extends `struct inode` with `enum op_inode_type` and a union pointing to either `struct device_node` or `struct property`.
- `is_string()` and `property_show()` format property values as printable strings, dot-separated bytes, or dot-separated 32-bit words.
- `openpromfs_lookup()` resolves child device nodes and properties under a firmware node.
- `openpromfs_readdir()` emits `.`, `..`, child nodes, then properties.
- `openprom_alloc_inode()`, `openprom_free_inode()`, and `openprom_iget()` manage the inode slab and `iget_locked()` lookup.
- `openprom_fill_super()`, `openpromfs_get_tree()`, `openpromfs_init_fs_context()`, `init_openprom_fs()`, and `exit_openprom_fs()` register and populate the filesystem.

### Control flow
Mount calls `get_tree_single()` and `openprom_fill_super()`, which creates the root inode with `OPENPROM_ROOT_INO`, sets directory inode/file operations, and stores `of_find_node_by_path("/")` in private inode data. Lookup and readdir both take `op_mutex`, walk `device_node` child and property lists, then create or find inodes using firmware-provided `unique_id` values. Property files open through `seq_open()` and print exactly one formatted record.

### State and persistence behavior
The filesystem has no persistent storage of its own. It mirrors the in-kernel OpenPROM/OpenFirmware device tree. Inode private data stores raw pointers to `device_node` and `property` objects, and root/noatime superblock settings avoid unnecessary timestamp behavior. Property reads are generated on demand.

### Dependencies and integration points
It depends on SPARC/OpenPROM headers and APIs: `asm/openprom.h`, `asm/oplib.h`, `asm/prom.h`, and OF node/property structures. It integrates with VFS through `file_system_type`, `fs_context_operations`, `super_operations`, `inode_operations`, `file_operations`, seq_file, simple statfs, and anon superblock teardown.

### Risks
The code assumes firmware node/property lists remain valid while exposed; `op_mutex` serializes traversal but does not by itself refcount individual properties. Property formatting uses raw typed loads for 32-bit output and is endian/alignment sensitive to firmware representation. The special `security-password` property is made owner read/write while most properties are read-only, so permission tests should verify that behavior.

### Test signals
Mounting openpromfs should show root node children as directories and node properties as files. Readdir should emit stable `.`/`..` plus children before properties. Reading string, byte-array, and word-array properties should match expected formatting. Module load/unload should register/unregister cleanly and free the inode cache after `rcu_barrier()`.
