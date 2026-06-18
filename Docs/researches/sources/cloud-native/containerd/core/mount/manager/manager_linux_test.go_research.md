<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/manager_linux_test.go -->
# sources/cloud-native/containerd/core/mount/manager/manager_linux_test.go

Purpose: Linux root integration tests for mount manager activation paths that perform real loopback, ext4, overlay, and temporary mounts.

Important APIs/types/functions: `TestLoopbackMount`, `TestLoopbackOverlay`, `TestTemporaryMountActivation`, `TestTemporaryOverlayMountActivation`, and helper `initalizeBlockDevice`.

Control flow: tests create temporary ext4 images with `mkfs.ext4`, mount and populate them via `fstest`, activate manager mount arrays, mount returned `ActivationInfo.System` mounts into a target, and compare resulting filesystem contents. Temporary activation tests assert the returned system mount is a bind mount sourcing the manager-created mounted tree.

State and persistence: uses temporary bbolt DBs, temporary target directories, real loop devices or loop mount options, and real mount namespaces; cleanup uses `Deactivate` and test unmount helpers.

Dependencies and integration points: requires root and Linux mount support; depends on external `mkfs.ext4`; exercises `LoopbackHandler`, `format` transformer, ordinary `mount.All`, and `WithTemporary`.

Risks covered: verifies transformed overlay lowerdir expressions point to mounted backing layers, separate loop handler and direct loop option flows both work, and temporary activations return a usable bind mount for `ctr images mount` style consumers.

Test signals: high-value integration coverage but environment-sensitive. It skips only by requiring root; failures can reflect kernel/filesystem/tooling availability rather than pure code regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/manager_linux_test.go -->
