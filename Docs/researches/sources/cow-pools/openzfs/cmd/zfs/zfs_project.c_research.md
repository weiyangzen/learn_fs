# File Research: sources/cow-pools/openzfs/cmd/zfs/zfs_project.c

`zfs_project.c` implements the file-tree worker used by `zfs project` in `zfs_main.c`. It lists, checks, clears, and sets project quota IDs and project-inherit flags on regular files and directories using ZFS-specific FS xattr ioctls.

Core data structure:
- `zfs_project_item_t` is a list node with a flexible trailing pathname buffer. It is used as a queue for iterative recursive directory traversal.

Main helpers:
- `zfs_project_item_alloc()` allocates and appends a queued directory path.
- `zfs_project_sanity_check()` stats the top-level target, restricts operations to regular files and directories, and rejects directory-only or recursive options on non-directories.
- `zfs_project_load_projid()` opens the top target and reads its current project ID with `ZFS_IOC_FSGETXATTR`; this supplies the expected project ID when the user did not pass `-p`.
- `zfs_project_handle_one()` opens one path, reads `zfsxattr_t`, and performs the selected operation:
  - list: prints project ID, inherit flag marker, and path.
  - check: reports paths whose project ID or inherit flag does not match expectations, optionally NUL-separated.
  - clear: clears `FS_XFLAG_PROJINHERIT` and optionally resets project ID to `ZFS_DEFAULT_PROJID`.
  - set: sets the expected project ID and optionally `FS_XFLAG_PROJINHERIT`.
  - mutations are applied with `ZFS_IOC_FSSETXATTR`.
- `zfs_project_handle_dir()` scans a directory, handles each regular file or directory child, and queues child directories when recursive mode is active.
- `zfs_project_handle()` is the exported entry point. It validates the target, derives the expected project ID when needed, handles the top path, and then breadth/depth iterates queued directories without recursive call stack growth.

Error behavior:
- Top-level missing/open/stat failures are reported.
- During directory traversal, `zpc_ignore_noent` is set so entries removed or renamed during traversal can be ignored.
- `ENOTSUP` during set emits a module/userspace version mismatch hint when the kernel version differs from `ZFS_META_ALIAS`.

Dependencies and integration:
- Uses `zfs_project_control_t` and operation constants from `zfs_projectutil.h`.
- Uses `ZFS_IOC_FSGETXATTR`, `ZFS_IOC_FSSETXATTR`, `zfsxattr_t`, `FS_XFLAG_PROJINHERIT`, and project ID constants from ZFS project quota headers.
- Uses `safe_malloc()` and `zfs_version_kernel()` from the broader `zfs` command support code.
- Called only by `zfs_do_project()` after CLI option validation.

Risks and maintenance notes:
- Recursive descent relies on `dirent.d_type == DT_DIR` for queuing subdirectories; filesystems that return unknown d_type may not recurse into those entries unless upstream behavior guarantees types here.
- Path construction checks against `PATH_MAX` before `asprintf()`, avoiding obvious overflow but still returning errors on very long names.
- Traversal is race-tolerant for disappearing children but not a transactional tree operation; concurrent renames can affect what is checked or updated.
