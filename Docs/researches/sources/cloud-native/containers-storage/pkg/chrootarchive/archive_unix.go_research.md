<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_unix.go -->
# sources/cloud-native/containers-storage/pkg/chrootarchive/archive_unix.go

Purpose: Unix non-Windows/non-Darwin reexec implementation for sandboxed archive unpacking and packing.

Important APIs/types/functions: `unpackDestination`, `procPathForFd`, `untar`, `newUnpackDestination`, `invokeUnpack`, `tar`, and `invokePack`. Constants define extra file descriptors 3 for tar options and 4 for root.

Control flow: parent `newUnpackDestination` opens the root directory as an fd and computes an absolute path inside the future chroot. `invokeUnpack` starts `storage-untar`, passes the archive on stdin, JSON-encodes `TarOptions` through fd 3, and passes the root fd as fd 4. Child `untar` locks its OS thread, reads options, fchdirs to fd 4 when using `/proc/self/fd/4`, chroots, unpacks to the relative dest, and flushes stdin. `invokePack` starts `storage-tar`, streams tar stdout through a pipe, and sends options as JSON stdin; child `tar` chroots and calls `archive.TarWithOptions`.

State/persistence: extraction mutates the chroot root; packing reads from it. Parent/child coordinate through pipes and inherited fds, not durable files.

Dependencies/integration: uses `reexec`, `archive.Unpack`, `archive.TarWithOptions`, JSON via `jsoniter`, Unix fd/chroot helpers, and root path safety from `archive.go`.

Risks: descriptor numbering is part of the ABI between parent and child. If child errors while upstream decompression is active, `invokeUnpack` drains input to avoid pipe deadlock. Path relativity and root fd handling are security-sensitive.

Test signals: huge exclude list test confirms options are not passed via argv/env. CVE symlink tests in `archive_unix_test.go` validate root confinement.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/pkg/chrootarchive/archive_unix.go -->
