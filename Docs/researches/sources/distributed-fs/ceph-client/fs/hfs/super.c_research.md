# sources/distributed-fs/ceph-client/fs/hfs/super.c

Purpose: implements classic HFS filesystem registration, mount context/options, superblock operations, delayed MDB flushing, statfs, remount validation, and inode cache lifecycle.

Important APIs and control flow: `hfs_sync_fs()` validates CNID counters and commits the MDB. `hfs_put_super()` cancels delayed work, marks the MDB clean, and releases MDB resources. `flush_mdb()` is delayed work that clears `work_queued` and commits dirty MDB/bitmap state. `hfs_mark_mdb_dirty()` schedules that work for writable mounts. `hfs_statfs()` reports block/free counts derived from allocation blocks and `fs_div`. `hfs_parse_param()` handles uid/gid, umasks, partition/session, creator/type, quiet, codepage, and iocharset. `hfs_fill_super()` initializes defaults/locks, calls `hfs_mdb_get()`, reads the root catalog record, instantiates root inode/dentry, and installs dentry ops. Module init creates the inode slab and registers `hfs`; exit unregisters and destroys the slab.

State and persistence: superblock fields, mount options, inode cache, delayed MDB work state, dirty MDB commits, and root dentry setup are managed here. Remount to read-write is refused if the MDB is not clean or is locked.

Dependencies and integration: integrates with Linux `fs_context`, block-device mount helpers, NLS, VFS super operations, `mdb.c`, `catalog.c`, `inode.c`, xattr handlers, and dentry operations.

Risks and test signals: mount failure paths call `hfs_mdb_put()` even after partial setup, so resource initialization order matters. Delayed MDB work is a persistence window. Tests should cover mount option parsing, failed NLS loads, read-only remount rules, statfs values, delayed dirty commit, and unmount after partial mount failure.
