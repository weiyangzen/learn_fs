<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_unix.go -->
# sources/cloud-native/containerd/pkg/archive/tar_unix.go

Purpose: non-Windows filesystem operations for tar extraction and creation: permissions, device headers, secure file opening, special files, xattrs, and parent metadata copy-up.

Important APIs and functions: `chmodTarEntry`, `setHeaderForSpecialDevice`, `open`, `openFile`, `mkdir`, `skipFile`, `handleTarTypeBlockCharFifo`, `getxattr`, `setxattr`, `copyDirInfo`, and `copyUpXAttrs`.

Control flow and state: regular files are opened then explicitly chmodded to bypass umask; directories are created then chmodded. Special tar entries become `mknod` calls unless user namespaces require skipping block/char devices. Xattrs are read/written with lget/lset behavior, trusted attrs are rejected or skipped, and parent copy-up preserves chown/chmod/timestamps/xattrs from lower parents.

Dependencies and integration: relies on `golang.org/x/sys/unix`, `moby/sys/userns`, `continuity/fs` and `continuity/sysx`. It supplies platform hooks used by `tar.go`.

Risks and test signals: root/user namespace behavior, xattr namespaces, NFS permission errors, and symlink no-follow timestamp/chmod behavior are sensitive. `tar_test.go` and Linux overlay tests cover many cases; platform-specific files cover FreeBSD differences.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/archive/tar_unix.go -->
