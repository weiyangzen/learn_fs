# File Research: sources/block-storage/parted/libparted/fs/jfs/jfs_types.h

JFS utility type and list-macro header. In `_JFS_UTILITY` mode it defines fixed-width signed/unsigned aliases, Unicode character type, OS/2 holdover aliases, a JFS timespec-like structure, boolean constants, min/max/roundup helpers, and JFS extent descriptor types.

It defines logical, physical, and data extent descriptors (`lxd_t`, `pxd_t`, `dxd_t`) with construction/extraction macros, including 24-bit length fields and little-endian address conversions. It also defines component-name and DASD quota structures.

The second half provides generic circular doubly-linked list and singly headed doubly-linked list macros: header/entry declarations, init, insert, remove, move-to-head/tail, and self-orphan helpers. For this file group, these definitions mainly support `jfs_superblock.h`; they are not actively used by `jfs.c` beyond providing type names.
