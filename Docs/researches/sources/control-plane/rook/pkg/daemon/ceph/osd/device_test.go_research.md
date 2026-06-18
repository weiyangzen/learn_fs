# sources/control-plane/rook/pkg/daemon/ceph/osd/device_test.go

This test file covers two related OSD helpers: bootstrap keyring creation and desired-device class assignment.

`TestOSDBootstrap` uses a temporary config directory and mock executor returning a key JSON payload. It calls `createOSDBootstrapKeyring()` and asserts that `bootstrap-osd/ceph.keyring` contains the bootstrap client header, key, and monitor caps. This indirectly verifies `init.go`'s template and integration with `cephclient.CreateKeyring()`.

`TestUpdateDeviceClass` checks the class priority order in `DesiredDevice.UpdateDeviceClass()`: preserve an explicit class, use PVC-backed environment class, fall back to sys disk type, use sys disk type for non-PVC when no store config is set, and prefer store config when provided.

State is test-local filesystem and environment variables. Dependencies include mock executor, temporary directories, Ceph cluster test info, operator OSD env var constants, and `sys.LocalDisk`. Gaps include no direct tests for `DeviceOsdMapping.String()`, `DesiredDevice` filter fields, or device class behavior with richer disk rotational metadata.
