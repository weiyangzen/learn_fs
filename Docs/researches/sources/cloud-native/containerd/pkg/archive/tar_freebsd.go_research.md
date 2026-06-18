<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_freebsd.go -->
# sources/cloud-native/containerd/pkg/archive/tar_freebsd.go

Purpose: FreeBSD-specific archive syscall helpers for node creation, xattr creation, and symlink-aware chmod.

Important APIs and functions: `mknod` calls FreeBSD's `unix.Mknod` signature with a `uint64` device; `lsetxattrCreate` calls `unix.Lsetxattr` without `XATTR_CREATE` and ignores unsupported/existing errors; `lchmod` uses `unix.Fchmodat(..., AT_SYMLINK_NOFOLLOW)`.

Control flow and state: no long-lived state. Each helper performs one filesystem syscall and adapts FreeBSD-specific signatures/errors to the generic archive flow.

Dependencies and integration: consumed by `tar_unix.go` and `tar.go` for special file extraction, parent xattr copy-up, and final mode restoration.

Risks and test signals: correctness depends on FreeBSD syscall semantics, especially symlink no-follow behavior and xattr error compatibility. Cross-platform tests may not exercise this unless FreeBSD CI is present.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_freebsd.go -->
