<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/copyup.rs -->
# sources/cloud-native/fuse-overlayfs/src/copyup.rs

Purpose: copy-up implementation that materializes lower-layer files/directories into the writable upper layer before modifications.

Important APIs and flow: `copy_xattr` copies extended attributes while skipping overlay-internal prefixes and tolerating unsupported/permission errors. `copy_data` tries `FICLONE`, then `sendfile`, then read/write fallback. `create_node_directory` recursively ensures parent directories are copied into upper, preserving ownership, timestamps, and xattrs via workdir temp names and safe renames. `copyup` handles directories, symlinks, special files, and regular files, creating objects in workdir then renaming into upper and updating node layer state.

State and persistence: writes temp files/directories in workdir and final objects in upperdir; removes related whiteouts where appropriate. Dependencies include `OvlLayer`, `NodeArena`, safe `openat2`, sys fs/io/xattr wrappers, and whiteout helpers. Risks include xattr buffer limits, partial cleanup on rename failures, file mode/ownership failures being ignored in places, and copy-up races with concurrent operations. Test signal should come from integration tests for copyup, xattr, special files, symlinks, and directory operations.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/copyup.rs -->
