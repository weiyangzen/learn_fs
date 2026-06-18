<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/direct.rs -->
# sources/cloud-native/fuse-overlayfs/src/direct.rs

Purpose: direct filesystem-backed `DataSource` implementation.

Important flow: `load_data_source` resolves the layer path, opens it as a trusted directory, records device ID, probes NFS file handle support, and detects stat override mode through xattrs. File operations use `openat2::safe_openat` or safe parent opening to keep resolution inside the layer root. `statat` and `fstat` prefer `statx` with fallback to `fstatat`/`fstat`; xattr operations use proc-fd paths for l* xattr calls; `get_nfs_filehandle` hashes kernel file handles when available.

State and persistence: holds an owned root fd, resolved path, device ID, stat override mode, NFS support state, and file handle size. It reads filesystem metadata/xattrs and opens files but does not write. Risks include proc-fd xattr path assumptions, NFS probe error handling, xattr detection ordering, and reliance on openat2 support wrappers. Test signal is integration coverage for path safety, xattrs, inode stability, and layer loading.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/src/direct.rs -->
