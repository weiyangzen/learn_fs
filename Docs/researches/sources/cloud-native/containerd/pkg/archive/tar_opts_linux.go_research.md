<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_opts_linux.go -->
# sources/cloud-native/containerd/pkg/archive/tar_opts_linux.go

Purpose: Linux-specific whiteout conversion for overlayfs-backed layers.

Important APIs and functions: `OverlayConvertWhiteout(hdr, path) (bool, error)` converts OCI/AUFS whiteouts to overlayfs representations.

Control flow and state: opaque directory marker `.wh..wh..opq` becomes `trusted.overlay.opaque=y` on the directory and is not written as a file. Per-file `.wh.<name>` becomes a character device at the target path via `unix.Mknod(..., S_IFCHR, 0)` followed by `os.Chown`, and the whiteout file itself is suppressed. Non-whiteout entries return `true`.

Dependencies and integration: used by callers passing `WithConvertWhiteout(OverlayConvertWhiteout)` to `Apply`, especially overlay snapshotter tests and layer application.

Risks and test signals: requires privileges for trusted xattrs, mknod, and chown; tests in `tar_linux_test.go` require root and overlayfs support. Incorrect conversion would make overlay lowerdir deletion semantics wrong.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_opts_linux.go -->
