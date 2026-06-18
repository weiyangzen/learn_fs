# sources/distributed-fs/ceph-client/fs/hfs/catalog.c

Purpose: implements classic HFS catalog B-tree key construction, record/thread creation, lookup-by-CNID, create/delete/move operations, and next-CNID correction after deletion.

Important APIs and control flow: `hfs_cat_build_key()` creates parent/name or CNID/thread keys after converting Linux names to Mac names. `hfs_cat_build_record()` builds file/folder records, while `hfs_cat_build_thread()` creates thread records used to resolve CNID to parent/name. `hfs_cat_create()` reserves btree nodes, inserts the thread record keyed by CNID, inserts the visible directory record keyed by parent/name, and rolls back the thread if visible insertion fails. `hfs_cat_find_brec()` reads a thread record and then searches for the visible record. `hfs_cat_delete()` removes the visible record, frees the resource fork for files, adjusts active readdir positions, removes the thread, decrements directory size, and corrects `next_id`. `hfs_cat_move()` copies the old visible record to a new parent/name, removes the old record, and rebuilds the thread.

State and persistence: catalog records, thread records, directory valence (`i_size`), root/file/folder counters indirectly, and `next_id` are modified. Updates dirty directory inodes and btree pages. CNID counts live in `hfs_sb_info` atomics and are eventually flushed to the MDB.

Dependencies and integration: uses `btree.h` search/mutation primitives, `hfs_asc2mac()`/`hfs_strcmp()` name handling, `hfs_free_fork()` extent cleanup, and open-directory state from `hfs.h`. VFS directory operations in `dir.c` are thin wrappers around these APIs.

Risks and test signals: multi-record catalog updates are not transactional, so interrupted rename/create/delete can leave orphaned thread or visible records. `hfs_correct_next_unused_CNID()` scans leaf nodes backward and depends on valid bnode offsets. Tests should cover create rollback, delete of files with resource forks, rename across directories, CNID wrap/corruption handling, and active `readdir()` during deletion.
