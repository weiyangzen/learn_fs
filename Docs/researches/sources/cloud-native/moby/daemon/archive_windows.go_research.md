## sources/cloud-native/moby/daemon/archive_windows.go

**Purpose:** Implements Windows-specific container filesystem archive operations used by `docker cp`, archive download/upload, and path stat APIs. It handles mounted rootfs and volume lifecycle while respecting Windows Hyper-V isolation limits.

**Important APIs:** `containerStatPath`, `containerArchivePath`, `containerExtractToDir`, `containerCopy`, and `isOnlineFSOperationPermitted` are daemon methods over `*container.Container`. They normalize slash paths to Windows paths, mount the container and volumes, resolve paths through container helpers, and use `chrootarchive` plus `archive` tar options.

**Control flow:** Each public helper locks the container, checks whether online filesystem access is permitted, mounts the rootfs, mounts volumes, resolves the requested path, performs stat/tar/untar work, logs an event, and then unmounts. Archive readers deliberately hold the container lock until the returned `ReadCloser` is closed by wrapping the underlying tar stream.

**State and persistence:** No durable state is created except extracted archive contents in the container filesystem. Temporary state consists of mount references, volume attachments, and deferred cleanup. Event log actions include `ArchivePath`, `ExtractToDir`, and `Copy`.

**Dependencies and integration:** Depends on daemon mount/unmount, container path resolution, `go-archive`, `chrootarchive`, compression, `errdefs`, and ioutils wrappers. It integrates with HTTP archive/copy endpoints and volume event logging.

**Risks:** Cleanup ordering is critical because leaked mounts or locks can wedge container operations. Windows drive-letter handling and symlink resolution are security-sensitive. `copyUIDGID` is silently ignored on Windows. Running Hyper-V containers reject online filesystem operations.

**Test signals:** This file has no adjacent direct test in this subset; coverage is likely endpoint/integration based. Useful regression cases include archive reader early close, symlink path rebasing, drive-letter extraction validation, and Hyper-V running-container rejection.
