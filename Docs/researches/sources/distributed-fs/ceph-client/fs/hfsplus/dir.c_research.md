# sources/distributed-fs/ceph-client/fs/hfsplus/dir.c

Purpose: provides HFS+ VFS directory operations, including lookup, readdir, hard links, unlink/rmdir, symlink, mknod/create/mkdir, rename, ioctl exposure, xattr listing, and file attribute operations.

Important APIs and control flow: `hfsplus_lookup()` searches the catalog by Unicode parent/name, resolves HFS+ hardlink alias records through the hidden directory (`iNode%d`), stores the visible CNID in `d_fsdata`, and instantiates the real inode. `hfsplus_readdir()` emits synthetic `.`/`..`, walks catalog records, converts Unicode names to Linux strings, hides the hidden directory, derives d_type from permissions, and stores active cursor state. `hfsplus_link()` converts the original file into a hidden inode record if needed, creates visible hardlink catalog records, increments nlink/file count, and writes affected catalog inodes. `hfsplus_unlink()` handles open-file temporary rename to hidden dir, visible alias deletion, nlink updates, hidden inode deletion when last link closes, and writeback. `hfsplus_rmdir()` checks emptiness and deletes folder records. `hfsplus_symlink()` and `hfsplus_mknod()` create new inodes, catalog records, optional security xattrs, instantiate dentries, and write back. `hfsplus_rename()` removes existing destination then calls catalog rename and writes involved inodes.

State and persistence: updates catalog tree, hidden-directory hardlink records, dentry `d_fsdata`, link counts, file counts, inode times, security xattrs, and dirty catalog/MDB state under `vh_mutex`.

Dependencies and integration: integrates `catalog.c`, `inode.c`, `attributes.c`/xattr security, Unicode conversion, random link id generation, and VFS operation tables.

Risks and test signals: hardlink conversion and open-unlink temporary renames are complex and non-transactional. Security xattr failure cleanup is best-effort. Tests should cover hardlink creation/deletion, open unlink, hidden dir hiding, symlink content persistence, device nodes, rename replacement, and active readdir with deletion.
