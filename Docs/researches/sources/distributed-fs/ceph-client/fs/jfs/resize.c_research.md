<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/resize.c -->
# sources/distributed-fs/ceph-client/fs/jfs/resize.c

## Purpose
`resize.c` implements online JFS filesystem growth through `jfs_extendfs`. It expands the usable aggregate, relocates/reformats inline log and fsck workspaces as needed, grows the block allocation map, optionally extends inode allocation map structures, and commits the new superblock geometry.

## Important APIs, types, and functions
The sole exported function here is `jfs_extendfs(struct super_block *sb, s64 newLVSize, int newLogSize)`. It uses `jfs_sb_info`, bmap and imap special inodes, `struct jfs_log`, `struct bmap`, superblock buffers, `lmLogFormat/lmLogShutdown/lmLogInit`, `txQuiesce/txResume`, `dbExtendFS/dbFinalizeBmap/dbSync`, `diExtendFS/diSync`, `xtAppend`, and special inode read/write helpers. Constants define bmap page sizing, megabyte units, and `BLKTODMAPN`.

## Control flow
The function first rejects non-growth, invalid device size, and read-only filesystems. It computes new inline log size, fsck workspace size/address, and filesystem size, ensuring the filesystem does not shrink. If the new inline log will not overlap the old volume area, it may preformat the log before quiescing. The filesystem is quiesced, the direct inode size is refreshed, and inline-log mounts shut down the old log, mark the superblock `FM_EXTENDFS`, record transitional descriptors, format/initialize the new log, then proceed to map growth.

Map growth is incremental. It extends the existing bmap coverage with `dbExtendFS`, grows the bmap file if more dmap pages are needed, appends bmap file extents from the newly added region using `xtAppend`, commits forced transactions, and loops until the new map size is covered. It finalizes the bmap, extends/syncs the imap only if AG size changed, syncs the bmap control page, copies the primary bmap inode to the secondary copy, and finally updates primary and secondary superblocks with clean final descriptors, new AG size, log serial, and fsck workspace metadata before resuming transactions.

## State and persistence behavior
Persistent state includes superblock size/log/fsck descriptors, `FM_EXTENDFS` transition marker, bmap file xtree and control pages, secondary bmap inode, imap AG metadata, inline log contents, and fsck workspace descriptors. Runtime state includes quiesced transaction state, log activation state, temporary buffers, and whether the inline log was already formatted.

## Dependencies and integration points
The function is invoked from remount/reconfigure parsing in `super.c`. It integrates with block-device sizing, buffer-head I/O, JFS log manager, transaction manager, xtree append logic, block map and inode map managers, special inode persistence, quota-neutral metadata growth, and crash recovery expectations in logredo/fsck.

## Risks and test signals
Risks include geometry arithmetic overflow, new log/fsck overlap, failure while `FM_EXTENDFS` is set, partial bmap growth requiring recovery, AG-size transitions, secondary-superblock write mistakes, and handling devices that cannot report size. Tests should grow with and without inline logs, specify explicit and default log sizes, cross dmap/AG boundaries, inject failures during log formatting, bmap append, imap sync, and superblock writes, and verify fsck/logredo can complete interrupted resize states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/jfs/resize.c -->
