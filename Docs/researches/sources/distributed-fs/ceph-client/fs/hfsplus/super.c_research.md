# sources/distributed-fs/ceph-client/fs/hfsplus/super.c

## Purpose
`super.c` implements HFS+ filesystem registration, fs_context setup, mount-time superblock initialization, metadata inode loading, volume-header commit/sync/unmount, inode-cache lifecycle, statfs, remount policy, and superblock teardown. It is the top-level coordinator for converting a block device with an HFS+ volume header into a live VFS superblock.

## Important APIs, types, and functions
Public functions are `hfsplus_iget()`, `hfsplus_mark_mdb_dirty()`, `hfsplus_prepare_volume_header_for_commit()`, and `hfsplus_commit_superblock()`. Important internal functions include `hfsplus_system_read_inode()`, `hfsplus_system_write_inode()`, `hfsplus_write_inode()`, `hfsplus_evict_inode()`, `hfsplus_sync_fs()`, `delayed_sync_fs()`, `hfsplus_put_super()`, `hfsplus_statfs()`, `hfsplus_reconfigure()`, `hfsplus_get_hidden_dir_entry()`, `hfsplus_fill_super()`, `hfsplus_alloc_inode()`, `hfsplus_free_inode()`, `hfsplus_get_tree()`, `hfsplus_free_fc()`, `hfsplus_init_fs_context()`, `hfsplus_kill_super()`, `hfsplus_init_once()`, `init_hfsplus_fs()`, and `exit_hfsplus_fs()`.

The file defines `hfsplus_sops`, `hfsplus_context_ops`, and `hfsplus_fs_type`, plus the `hfsplus_icache` slab.

## Control flow
Module initialization creates the inode cache, creates the attribute-entry cache, and registers the `hfsplus` filesystem type. New mount contexts allocate `hfsplus_sb_info`, fill defaults for normal mounts, and install parse/get_tree/reconfigure/free callbacks. `get_tree_bdev()` calls `hfsplus_fill_super()`.

Mount setup initializes locks and delayed sync work, loads an NLS table, temporarily switches to UTF-8 to locate the hidden directory, reads the wrapper/volume header, validates HFS+ version and size limits, sets `s_op` and max file size, enforces readonly policy for unclean, softlocked, or journaled volumes unless force permits, opens extents/catalog/optional attributes B-trees, loads the allocation file and root inode, installs dentry operations, finds or creates the hidden directory for deleted open files, prepares and syncs the volume header when writable, restores the requested NLS table, and unwinds resources on errors.

`hfsplus_iget()` initializes private inode fields for new inodes, then reads user/root CNIDs from the catalog tree or system CNIDs from volume-header fork records. Writeback first writes dirty overflow extents, then writes either catalog records or system fork records. System B-tree inodes also force a B-tree header write under the nested tree lock.

`hfsplus_sync_fs()` explicitly writes catalog, extents, attributes, and allocation mappings, commits the volume header, and issues a cache flush unless barriers are disabled. `hfsplus_mark_mdb_dirty()` queues delayed sync work for dirty volume-header state. Unmount cancels delayed work, marks writable volumes unmounted and consistent, syncs, drops metadata inodes/B-trees/buffers, and later frees NLS and private superblock state via RCU from `kill_super`.

## State and persistence behavior
Persistent state is centered on the primary and backup volume headers plus metadata files referenced by the volume header. `hfsplus_prepare_volume_header_for_commit()` writes mount version, modify date, increments write count, clears `HFSPLUS_VOL_UNMNT`, and sets `HFSPLUS_VOL_INCNSTNT`; unmount reverses those consistency bits before syncing. `hfsplus_commit_superblock()` copies runtime counters into the volume header under `vh_mutex` and `alloc_mutex`, writes the primary header, and writes the backup header only when `HFSPLUS_SB_WRITEBACKUP` was set.

Because writable journaled HFS+ is not supported, this implementation relies on conservative readonly policy, explicit writeback, volume-header consistency flags, delayed syncing, and optional flush barriers. Error paths carefully drop loaded B-trees, inodes, headers, and NLS tables.

## Dependencies and integration points
The file integrates with Linux module and filesystem registration, block-device mounts, fs_context, VFS super operations, writeback, NLS, slab/RCU, catalog/extents/attributes/allocation implementations, xattr handlers, wrapper volume-header reading, security initialization for the hidden directory, and option parsing from `options.c`.

## Risks and test signals
Risks include write access to journaled or unclean volumes with `force`, incomplete error unwinding, delayed sync races during unmount, backup volume-header update conditions, lock ordering between `vh_mutex`, `alloc_mutex`, and B-tree locks, hidden-directory creation failures, temporary NLS switching side effects, and non-journaled consistency windows. Test signals include clean/unclean/softlocked/journaled mount policy, force mounts, remount readwrite checks, volume size overflow rejection, missing or malformed B-trees, hidden directory absent/present/wrong type, sync/unmount consistency flags, backup-header updates, statfs counters, inode cache lifecycle, and module init/exit failures.
