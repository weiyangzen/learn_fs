## sources/distributed-fs/beegfs/meta/source/toolkit/StorageTkEx.cpp

Purpose: Adds metadata-server-specific storage toolkit behavior: storage-format validation and incremental contained-directory ID listing for fsck.

Important APIs/types/functions: `createStorageFormatFile()` writes format properties including `xattr=true/false`. `checkStorageFormatFile()` loads/upgrades a format file and rejects missing or mismatched xattr settings. `getContDirIDsIncremental()` lists metadata dentry hash directories incrementally using `seekdir()`/`d_off`. `getNextContDirID()` is a one-entry wrapper.

Control flow: Format creation reads config from `Program::getApp()`. Format checking loads properties and throws `InvalidConfigException` on missing `xattr` or config mismatch. Directory iteration computes hash subdirs, opens the directory, seeks to the caller's offset, filters entries, skips the root dir on non-root MDS, and returns the next offset.

State and persistence: Reads/writes the metadata storage format file and scans persistent dentry directory names. Does not lock fsck listing paths, as noted by the source comment.

Dependencies and integration: Depends on metadata `App`, `Config`, `StorageTk`, `MetaStorageTk`, `StorageTkEx.h`, POSIX directory APIs, and root-node/mirror-group state from the app.

Risks and test signals: `seekdir()` offsets are filesystem-specific and can become stale if directories mutate during fsck. No locking means concurrent metadata changes may cause missing or duplicate IDs. Tests should cover xattr format mismatch, root-dir skip behavior for mirrored/non-mirrored paths, incremental pagination, and opendir/readdir error handling.
