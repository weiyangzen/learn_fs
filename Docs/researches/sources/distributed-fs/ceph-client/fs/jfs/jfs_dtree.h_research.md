# sources/distributed-fs/ceph-client/fs/jfs/jfs_dtree.h

Purpose: declares the on-disk/in-memory directory dtree layout and the exported directory tree APIs used by JFS directory operations.

Important APIs and types: defines `ddata_t`, `struct dtslot`, `struct idtentry`, `struct ldtentry`, `struct dir_table_slot`, `dtroot_t`, and `dtpage_t`. It declares `dtInitRoot`, `dtSearch`, `dtInsert`, `dtDelete`, `dtModify`, `jfs_readdir`, `check_dtroot`, and `check_dtpage`. Important macros include `DO_INDEX`, `PARENT`, `dtEmpty`, `DT_GETSTBL`, `NDTINTERNAL`, `NDTLEAF`, `NDTLEAF_LEGACY`, `DTSaddress`, and `addressDTS`.

Control flow: callers use the declared APIs as the directory lifecycle: initialize root, search before insert/remove/rename, mutate entries, and enumerate through `jfs_readdir`. The layout macros drive slot counts, sorted-table addressing, parent lookup, and persistent directory index addressing.

State and persistence behavior: this header defines the serialized directory structures. `dtroot_t` resides inside the JFS inode and carries the parent inode number, sorted table, freelist, and DASD accounting. `dtpage_t` describes external dtree pages with sibling pointers and a self PXD. `ldtentry` has a legacy format without persistent index and an indexed format with the `index` field. `dir_table_slot` records whether a readdir index is valid or free and stores either a leaf page/slot pair or a next-free/deleted index.

Dependencies and integration: depends on `jfs_btree.h`, JFS PXD types, `struct inode`, and superblock mount flags through `JFS_SBI`. It is consumed by directory operations, inode incore layout (`jfs_incore.h` embeds `dtroot_t` and `dir_table_slot`), inode serialization, and VFS directory file operations.

Risks and edge cases: slot-size constants must match the packed structures exactly or tree mutation will corrupt on-disk directories. `DO_INDEX` changes both entry format and `i_size` semantics, so mixed legacy/indexed handling must choose `NDTLEAF_LEGACY` versus `NDTLEAF` correctly. `DIREND` uses `INT_MAX`, making persistent cookie bounds important.

Test signals: compile-time layout users, indexed versus legacy directory creation, large names requiring continuation slots, parent lookup through `PARENT`, and directory root/page corruption checks are the relevant signals.
