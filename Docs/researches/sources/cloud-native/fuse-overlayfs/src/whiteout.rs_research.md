# sources/cloud-native/fuse-overlayfs/src/whiteout.rs

## Purpose
`whiteout.rs` implements overlay whiteout and opaque-directory operations for both privileged kernel-overlay style and unprivileged fallback style.

## Important APIs, Types, And Functions
`is_directory_opaque` detects opacity via `trusted.overlay.opaque`, `user.overlay.opaque`, `user.fuseoverlayfs.opaque`, or `.wh..wh..opq`. `set_fd_opaque` writes an opaque xattr and creates the sentinel file. `delete_whiteout` removes existing char-device and `.wh.<name>` whiteouts. `create_whiteout` creates a char device `(0,0)` when allowed, otherwise falls back to a regular `.wh.<name>` file. Static `CAN_MKNOD` disables future mknod attempts after permission/support failures.

## Control Flow
Directory merge code calls `is_directory_opaque` to stop lower-layer lookup. Creation and rename paths call `delete_whiteout` when recreating a name. Removal and lower-layer rename paths call `create_whiteout` to hide lower entries. New directories under copied-up lower parents call `set_fd_opaque` so old lower contents do not reappear.

## State And Persistence
Persistent state is encoded as xattrs, `.wh..wh..opq` sentinel files, char-device `(0,0)` whiteouts, or `.wh.<name>` files in the upper layer. In-memory state is limited to `CAN_MKNOD`, which records process-wide fallback from mknod to `.wh.` files.

## Dependencies And Integration Points
The module depends on datasource xattr/file-existence APIs, `sys::fs`, `sys::xattr`, `sys::openat2`, and constants from `xattr.rs`. It is tightly integrated with `overlay.rs` directory loading, deletion, mkdir, create, link, and rename behavior.

## Risks
Privilege and filesystem differences mean mknod and trusted xattrs can fail; fallback logic must remain correct. Whiteout deletion must avoid removing non-whiteout real files. Opaque detection order affects multi-layer merge semantics. Sentinel creation through `safe_openat` requires openat2 support. `CAN_MKNOD` is global, so one EPERM/ENOTSUP switches the process to fallback whiteouts for later operations.

## Test Signals
`test-dir-ops.sh` covers opaque xattrs, `.wh..wh..opq`, char-device or `.wh.` whiteouts, rmdir whiteouts, mkdir over whiteouts, and readdir filtering. `test-rename.sh` validates whiteout creation for renamed lower files. `fedora-installs.sh` includes regressions for multi-layer whiteouts and opaque sentinels.
