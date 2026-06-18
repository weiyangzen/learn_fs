# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_symlink.c

## Purpose
Implements symlink creation, symlink target caching, mountpoint text handling, and readlink.

## Important APIs, Types, and Functions
`afs_symlink` creates new symlinks or mountpoints. `afs_DisconCreateSymlink` writes disconnected symlink contents to a cache chunk. `afs_MemHandleLink` and `afs_UFSHandleLink` load symlink or mountpoint text into `vcache->linkData` from memory or UFS cache backends. `afs_readlink` verifies and returns cached link text through `AFS_UIOMOVE`.

## Control Flow and State
`afs_symlink` creates a request, fakestats the parent, checks name and target lengths, handles dynroot symlinks or readonly dynroot mount failures, verifies parent status, rejects readonly/offline-without-RW cases, prepares store status mode bits, and gets the parent directory dcache. Connected mode calls `RXAFS_Symlink` or `RXAFS_DFSSymlink` for foreign cells. Disconnected RW mode generates a fake FID. If the directory can be updated locally, it inserts the new name in the parent dcache. It then creates a new vcache under `afs_xvcache`, sets callback/status state, processes server status or generates disconnected status, stores `linkData`, and returns or releases the new vcache. `afs_readlink` verifies/fakestats the vnode, requires `VLNK`, calls `afs_HandleLink`, and copies the string to the caller.

Connected symlink creation is persisted synchronously by the fileserver. Disconnected creation writes the target into the local dcache chunk, marks the vcache dirty with `VDisconCreate`, and relies on replay. `linkData` caches a null-terminated target string. Mountpoint-style targets starting with `#` or `%` and ending in `.` are stored with mode `0644`; ordinary symlinks use `0755` and include a terminating null.

## Dependencies and Integration Points
Depends on fileserver symlink RPCs, directory dcache updates, `afs_LocalHero`, callback queues, volume references, cache backends, dynroot hooks, disconnected status generation, fakestat, and `afs_HandleLink`, which selects memory or UFS link loading through cache type integration.

## Risks and Test Signals
Link target loading rejects cached link data longer than 1024 bytes. The creation path holds global vcache state while initializing the new vcache, so callback and vcache lock ordering matters. In disconnected mode, failure after parent directory insertion is called out as needing cleanup. Mountpoint text conventions depend on mode bits and trailing dot handling.

Test ordinary symlinks, mountpoint-style symlinks, long names/targets, dynroot symlink creation, readonly and disconnected failures, disconnected RW creation and replay flags, local directory cache update success/failure, readlink cache hit/miss for UFS and memory cache, non-link readlink `EINVAL`, and foreign/DFS callback handling.
