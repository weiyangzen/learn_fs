# sources/distributed-fs/openafs/src/WINNT/afsd/cm_freelance.h

Purpose: declares the public freelance fake-root interface used by Windows cache-manager initialization, pioctl handling, scache metadata fetch, and optional CellServDB import.

Important APIs/types/functions: `cm_localMountPoint_t` stores a fake-root child name, a mount-point or symlink target string, and a cache-manager file type. Initialization and lifecycle APIs are `cm_InitLocalMountPoints`, `cm_InitFreelance`, `cm_FreelanceShutdown`, `cm_reInitLocalMountPoints`, and `cm_FreelanceImportCellServDB`. Change tracking is exposed with `cm_noteLocalMountPointChange`, `cm_getLocalMountPointChange`, and `cm_clearLocalMountPointChange`. Mutation and query APIs cover mount points and symlinks: `cm_FreelanceAddMount`, `cm_FreelanceRemoveMount`, `cm_FreelanceMountPointExists`, `cm_FreelanceAddSymlink`, `cm_FreelanceRemoveSymlink`, and `cm_FreelanceSymlinkExists`. Scache helpers are `cm_FreelanceFetchMountPointString`, `cm_FreelanceFetchFileType`, and `cm_FakeRootFid`.

State and persistence: exposes `FakeFreelanceModTime`, `cm_freelanceEnabled`, `cm_freelanceImportCellServDB`, and `cm_freelanceDiscovery`. Defines `AFS_FREELANCE_INI` for legacy migration and fake root cell/volume IDs as `0xFFFFFFFF`.

Dependencies and integration: depends on cache-manager types such as `cm_fid_t` and `cm_scache_t` supplied by surrounding headers. The header is consumed by `cm_freelance.c`, pioctl handlers in `cm_ioctl.c`, and fake-root aware cache and redirector paths.

Risks: the API passes mutable `char *` strings and does not encode buffer lengths; callers must honor the implementation's locking assumptions and fake-root FID conventions.

Test signals: compile coverage with `AFS_FREELANCE_CLIENT` enabled, pioctl add/remove flows, fake-root FID comparison, and scache mount-point/file-type fetches.
