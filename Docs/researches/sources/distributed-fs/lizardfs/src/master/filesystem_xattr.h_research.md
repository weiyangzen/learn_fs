# sources/distributed-fs/lizardfs/src/master/filesystem_xattr.h

Purpose: defines xattr hash-table structures, hash functions, validation helpers, and the public xattr manipulation API.

Important APIs/types/functions: constants define inode/data hash sizes and checksum seed; `xattr_data_entry` stores one attribute with links in both hash indexes and frees name/value in its destructor; `xattr_inode_entry` aggregates an inode's attributes and list/value lengths; `xattr_data_hash_fn()` and `xattr_inode_hash_fn()` compute table indexes; public functions cover checksum integration, list/get/set/remove, and checksum recalculation.

Control flow: callers use hash helpers indirectly through implementation functions. `xattr_namecheck()` rejects embedded nulls outside metarestore builds.

State and persistence behavior: the structs are the in-memory persisted model loaded from metadata sections. The header also declares `void free(xattr_data_entry *)` to prevent accidental C-style freeing of entries that need destructors.

Dependencies/integration: used by filesystem xattr operations and metadata store load/save. It depends on platform constants such as `MFS_XATTR_SIZE_MAX`, `MFS_XATTR_LIST_MAX`, and xattr set modes.

Risks and test signals: fixed hash sizes assume power-of-two masks; manual ownership is split between `new/delete` for data entries and `malloc/free` for inode entries. Tests should include memory-safety paths and hash collision behavior.
