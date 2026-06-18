## sources/distributed-fs/beegfs/client_module/source/toolkit/InodeRefStore.c

**Purpose:** Provides the pointer comparator used by `InodeRefStore`'s red-black tree.

**Important APIs/types/functions:** Implements `__InodeRefStore_keyComparator`, ordering inode pointer keys by address.

**Control flow:** Returns -1, 0, or 1 based on raw pointer comparison.

**State and persistence behavior:** No state is stored in this file.

**Dependencies and integration points:** The comparator is passed to `PointerRBTree_init` in `InodeRefStore_init` and determines ordering for inode reference tracking.

**Risks:** Ordering by pointer address is suitable only for identity, not inode number or lifetime ordering. Reused inode memory addresses after removal are fine because the store holds references while entries exist.

**Test signals:** Tree insertion/removal tests should confirm duplicate pointer detection and stable iteration ordering while references are held.
