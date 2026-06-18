# sources/distributed-fs/ceph-client/fs/hfsplus/catalog.c

Purpose: implements HFS+ catalog key ordering/building, catalog record/thread creation, CNID lookup, directory subfolder counters, create, delete, and rename.

Important APIs and control flow: `hfsplus_cat_case_cmp_key()` and `hfsplus_cat_bin_cmp_key()` compare by parent CNID then Unicode name, using casefold or binary comparison. `hfsplus_cat_build_key()` converts Linux names to HFS+ Unicode keys; `hfsplus_cat_build_key_with_cnid()` builds thread keys. `hfsplus_cat_set_perms()` serializes Linux mode/uid/gid/flags/rdev/nlink into HFS+ permission records. `hfsplus_cat_build_record()` creates folder/file records, including special hardlink alias records. `hfsplus_fill_cat_thread()` creates variable-size thread records. `hfsplus_find_cat()` resolves CNID through a thread to the visible record. `hfsplus_create_cat()` inserts thread and visible record with rollback. `hfsplus_delete_cat()` removes visible and thread records, frees resource forks, adjusts readdir cursors, updates subfolder counts, and deletes xattrs. `hfsplus_rename_cat()` inserts destination visible record, removes source visible/thread records, and creates a new thread.

State and persistence: mutates catalog tree pages, directory `i_size`, HFSX subfolder counters, inode times, catalog-tree dirty flag, and directory inode dirty flags. File/folder records persist permissions, Finder info, fork metadata, and hardlink metadata.

Dependencies and integration: uses HFS+ btree search/mutation, Unicode conversion, extent fork cleanup, xattr deletion, inode dirty marking, and directory open cursor lists.

Risks and test signals: create/delete/rename are multi-record and not journaled. Hardlink alias semantics depend on hidden directory state. Tests should cover Unicode names, HFSX subfolder counters, hardlink records, rename across dirs, resource-fork delete, xattr delete-all, and rollback after failed second insert.
