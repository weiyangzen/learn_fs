## sources/distributed-fs/alluxio/underfs/local/src/main/java/alluxio/underfs/local/LocalUnderFileSystem.java

### Purpose
`LocalUnderFileSystem` adapts the local POSIX filesystem to Alluxio's `ConsistentUnderFileSystem` interface for tests, single-node mode, or shared mounted filesystems.

### Important APIs, Types, And Functions
Core overrides include `create`, `createDirect`, `deleteDirectory`, `deleteFile`, `exists`, `getBlockSizeByte`, `getDirectoryStatus`, `getFileLocations`, `getFileStatus`, `getSpace`, `getStatus`, `isDirectory`, `isFile`, `listStatus`, `mkdirs`, `open`, `renameFile`, `renameDirectory`, `setOwner`, `setMode`, `connectFromMaster`, `connectFromWorker`, and `supportsFlush`. Nested `LocalOutputStream` exposes approximate content hashes.

### Control Flow
Paths are normalized by stripping any URI scheme. Creates optionally create parents, open buffered local output streams, and set permissions. Recursive deletes walk children before deleting the directory. Status calls read POSIX attributes and translate permissions. `mkdirs` builds missing parent stack to apply mode and ownership. `open` uses `ByteStreams.skipFully` for offsets. Listing optionally filters broken symlinks before reading attributes.

### State, Persistence, And Dependencies
State is just the inherited configuration and `mSkipBrokenSymlinks`. Persistent state is the local filesystem. Dependencies include Java `File`, NIO POSIX attributes, Alluxio path/status/options utilities, permission utilities, and network utilities for local file location.

### Integration Points
`LocalUnderFileSystemFactory` selects this class for local paths. It implements `AtomicFileOutputStreamCallback`, so atomic writes use Alluxio's atomic output wrapper.

### Risks
POSIX attribute reads can fail on non-POSIX filesystems. `File.renameTo` has platform-specific semantics and weak error reporting. Recursive delete uses `File.list`, which may return null on IO errors and then proceeds to delete the parent. Owner changes can be ignored depending on configuration, potentially diverging Alluxio metadata from local permissions.

### Test Signals
`LocalUnderFileSystemTest` covers create/delete/mkdir/open/rename/status/location/mode behavior, symlink skip configuration, operation mode, and async listing counts.
