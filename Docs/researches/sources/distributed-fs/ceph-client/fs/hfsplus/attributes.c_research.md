# sources/distributed-fs/ceph-client/fs/hfsplus/attributes.c

Purpose: implements HFS+ attribute-tree support for extended attributes, limited to inline data records. It handles key creation, lookup, existence checks, create, delete, delete-all, and replace.

Important APIs and control flow: `hfsplus_create_attr_tree_cache()`/`destroy` manage a slab cache for temporary `hfsplus_attr_entry` records. `hfsplus_attr_bin_cmp_key()` orders attributes by CNID then Unicode attribute name. `hfsplus_attr_build_key()` converts xattr names to HFS+ Unicode xattr keys and computes variable key length. `hfsplus_attr_build_record()` supports `HFSPLUS_ATTR_INLINE_DATA`, rejects oversized inline values with `-E2BIG`, and treats fork/extents records as unsupported placeholders. `hfsplus_find_attr()` searches either an exact name or first record for a CNID. `hfsplus_create_attr()` reserves btree space and inserts an inline record. `__hfsplus_delete_attr()` validates CNID and record type before removal. `hfsplus_delete_all_attrs()` loops over first-by-CNID records. `hfsplus_replace_attr()` deletes then recreates.

State and persistence: mutates the attributes btree and marks both the attributes-tree inode and target inode with `HFSPLUS_I_ATTR_DIRTY`. Attribute data is persisted inline in btree leaf records; non-inline attribute forks are not supported.

Dependencies and integration: uses HFS+ btree search/mutation helpers, Unicode conversion, xattr constants from `xattr.h`, and raw HFS+ attribute structures. VFS xattr handlers call these helpers indirectly.

Risks and test signals: replace is delete-then-create without transaction rollback. Delete-all relies on repeated first-by-CNID searches after each removal. Tests should cover absent attribute tree, exact and first-by-CNID lookup, max inline data size, unsupported fork/extents records, replace failure after delete, and Unicode xattr names.
