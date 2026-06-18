# sources/distributed-fs/ceph-client/fs/hfs/hfs.h

Purpose: small classic HFS private header that includes common HFS on-disk definitions and declares `struct hfs_readdir_data`, the per-open-directory cursor state used to keep directory iteration coherent during catalog mutations.

Important types and APIs: `struct hfs_readdir_data` stores a list node, owning `struct file *`, and the last catalog key seen by `readdir()`. It has no functions of its own; it is allocated in `hfs_readdir()`, linked under `HFS_I(dir)->open_dir_lock`, consulted in `hfs_cat_delete()` to decrement `f_pos` for affected readers, and freed in `hfs_dir_release()`.

State and persistence: the structure is in-memory only. It does not persist to disk, but it protects the user-visible stream position while persistent catalog records are removed from the underlying B-tree.

Dependencies and integration: includes `<linux/hfs_common.h>` for shared HFS/HFS+ raw definitions such as catalog keys and constants. It is included by `hfs_fs.h`, making the readdir state available to directory and catalog code.

Risks and test signals: because the state stores a catalog key copied from a mutable B-tree position, correctness depends on catalog comparator stability and locking between directory iteration and deletion. Tests should run `readdir()` while deleting and renaming entries in the same directory and validate no stale list entries remain after file release.
