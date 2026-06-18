## sources/distributed-fs/beegfs/meta/source/storage/DirEntry.cpp

Purpose: implements dentry persistence, update, removal, loading, type probing, inode extraction, and initial storage for BeeGFS metadata directory entries.

Important functions: `storeInitialDirEntryID`, `storeInitialDirEntryName`, `storeUpdatedDirEntryBuf*`, `storeUpdatedDirEntry`, `storeUpdatedInode`, `removeDirEntryFile`, `removeDirEntryName`, `removeDirEntryID`, `removeBusyFile`, `loadFromFileName`, `loadFromID`, `loadFromFile*`, `loadEntryTypeFromFile*`, `createFromFile`, `createInodeByID`, and `storeInitialDirEntry`.

Control flow: initial storage first creates an entry-by-ID file containing serialized dentry metadata, then hard-links it to the user-visible entry-by-name. For directories or non-inlined inodes, the ID file is unlinked after the name link is created. Updates serialize through `DiskMetaData` and write either to xattr `META_XATTR_NAME` or file contents based on config. Loads mirror that choice. Removal deletes name and/or ID paths; busy inlined-file removal moves the ID file into the inode hash directory, links it into disposal, and deletes the visible dentry as requested.

State and persistence behavior: dentry metadata can live either in extended attributes or file contents. Inlined file inode data is embedded in the dentry metadata; non-inlined inodes are represented by separate inode files. Buddy-mirrored dentries record changes in the current `BuddyResyncer` changeset as dentry or inode modifications/deletions. Empty dentry files can be self-healed by removal if configured.

Dependencies and integration points: depends on `Program` for config and app paths, `MetaStorageTk` path builders, `DiskMetaData` serialization, `FileInode`, `BuddyResyncer`, POSIX link/unlink/rename/xattr I/O, and disposal directories from `App`.

Risks: `storeUpdatedDirEntry` writes to `dirEntryPath + "/" + name` despite comments warning never to update through entry-name paths except fsck; this should be reconciled with call-site expectations. Initial storage is not rename-atomic and compensates manually on failures. `storeUpdatedDirEntryBufAsContents` uses in-place writes and truncation, so a crash during update can leave partial metadata. Type probing reads a single byte without full validation. Busy-file removal ignores errors from disposal linking. Xattr and file-content paths have separate error behavior and self-healing logic.

Test signals: create/link rollback on `EEXIST` and write failure, xattr and contents modes, empty-file self-heal, busy inlined inode unlink, buddy-resync changeset entries, load invalid/corrupt serialized dentries, type probing, and crash/partial-write recovery behavior.
