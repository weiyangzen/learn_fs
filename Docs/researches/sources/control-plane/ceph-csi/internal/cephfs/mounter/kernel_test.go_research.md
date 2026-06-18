## sources/control-plane/ceph-csi/internal/cephfs/mounter/kernel_test.go

Purpose: Unit test for filesystem support detection used by kernel mounter initialization.

Important flow: `TestFilesystemSupported` installs a test error logger, asserts `filesystemSupported("proc")` is true because proc is expected in `/proc/filesystems`, and asserts a made-up filesystem name is false.

State and dependencies: Reads the host `/proc/filesystems`; no Ceph state or mounts are involved. Uses `testify/require`.

Risks and signal: The test covers parser basics and failure reporting but does not validate Ceph module availability, modprobe, or mount command construction. It assumes procfs is present, which is valid for normal Linux CI but not for exotic environments.
