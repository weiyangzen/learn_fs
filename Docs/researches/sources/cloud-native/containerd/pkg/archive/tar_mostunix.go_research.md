<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_mostunix.go -->
# sources/cloud-native/containerd/pkg/archive/tar_mostunix.go

Purpose: Unix helper implementation for non-Windows, non-FreeBSD platforms.

Important APIs and functions: `mknod`, `lsetxattrCreate`, and `lchmod`. `mknod` adapts `unix.Mknod` device type to `int`; `lsetxattrCreate` uses `XATTR_CREATE` and treats unsupported/no-data/existing as ignorable; `lchmod` skips symlinks and chmods regular paths.

Control flow and state: stateless wrappers around Unix filesystem syscalls.

Dependencies and integration: supplies functions called from `tar_unix.go` for special files, xattr copy-up, and final archive mode application.

Risks and test signals: skipping chmod for symlinks avoids following links during extraction. The xattr function deliberately ignores already-existing attrs during parent copy-up, preventing parent metadata copy from overwriting newly created attributes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_mostunix.go -->
