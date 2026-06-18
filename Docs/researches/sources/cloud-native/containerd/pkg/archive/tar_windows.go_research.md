<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_windows.go -->
# sources/cloud-native/containerd/pkg/archive/tar_windows.go

Purpose: Windows implementation of archive filesystem hooks for generic tar apply/diff.

Important APIs and functions: `chmodTarEntry`, `setHeaderForSpecialDevice`, `open`, `openFile`, `mkdir`, `skipFile`, `handleTarTypeBlockCharFifo`, `lchmod`, `getxattr`, `setxattr`, `copyDirInfo`, and `copyUpXAttrs`.

Control flow and state: permissions are masked to 0755 and execute bits are added; file opens use `moby/sys/sequential` to avoid standby-list pressure; colon-containing filenames are skipped; special devices, lchmod, xattrs, and xattr copy-up are no-ops or unsupported.

Dependencies and integration: used by `tar.go` on Windows for non-hcsshim generic tar paths. Windows container layer-specific behavior is in `tar_opts_windows.go`.

Risks and test signals: skipping colon names is a compatibility compromise for pulling Linux images during development. Xattrs from archives fail as unsupported, so Windows archives should not contain them. Windows-specific tests are mostly in IO/log URI files, not archive extraction.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_windows.go -->
