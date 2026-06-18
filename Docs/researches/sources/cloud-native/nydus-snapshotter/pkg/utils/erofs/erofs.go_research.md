<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/erofs/erofs.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/erofs/erofs.go

Purpose: wraps Linux EROFS mount/unmount operations for fscache-backed nydus filesystems and derives stable fscache IDs.

Important APIs: `Mount(domainID, fscacheID, mountpoint)`, `Umount(mountPoint)`, and `FscacheID(snapshotID)`. `Mount` builds either `domain_id=<domain>,fsid=<id>` for shared domains or `fsid=<id>` otherwise, then calls `unix.Mount("erofs", mountpoint, "erofs", 0, opts)`.

Control flow and state: the functions are stateless wrappers around kernel syscalls. On `EINVAL` with a domain ID, `Mount` logs a hint that shared domains require Linux kernel >= 6.1.

Dependencies/integration: uses `golang.org/x/sys/unix`, containerd logging, go-digest, and pkg/errors. `FscacheID` hashes `nydus-snapshot-<snapshotID>` to avoid raw snapshot IDs as fs cache IDs.

Risks and test signals: requires Linux EROFS/fscache support and mount privileges. Kernel compatibility is only logged, not feature-detected. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/erofs/erofs.go -->
