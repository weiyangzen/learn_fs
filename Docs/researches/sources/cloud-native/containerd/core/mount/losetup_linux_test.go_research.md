# sources/cloud-native/containerd/core/mount/losetup_linux_test.go

Purpose: integration tests for Linux loop device setup and cleanup behavior.

Important APIs and helpers: `createTempFile`, `TestNonExistingLoop`, `TestRoLoop`, `TestRwLoop`, `TestAttachDetachLoopDevice`, `TestAutoclearTrueLoop`, and `TestAutoclearFalseLoop`.

Control flow: each test requires root. Temporary backing files are truncated to 512 bytes. Tests verify missing file errors, readonly loop write rejection, read-write loop writes, attach/detach helper success, autoclear cleanup after closing the loop fd, and manual removal when autoclear is false.

State and persistence: uses real `/dev/loop*` devices and kernel loop state. Autoclear test compares backing inode through `IoctlLoopGetStatus64` until the device is cleared or retries expire.

Dependencies and integration: depends on root privileges, testutil, unix ioctls, filesystem stat data, and `losetup_linux.go` helpers.

Risks: environment-sensitive due to loop device availability and permissions. Autoclear polling has timing assumptions and can fail on slow cleanup. Tests manipulate real loop devices, so cleanup correctness is important.

Test signals: strong integration signal for loop setup flags and cleanup behavior.
