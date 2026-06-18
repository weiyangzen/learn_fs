<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/run/run_unix.go -->
# sources/cloud-native/containerd/cmd/ctr/commands/run/run_unix.go

## Purpose
Unix/Linux container construction for `ctr run`, including image unpacking, snapshots, namespaces, security, resources, devices, CDI/GPU, and runtime options.

## Important APIs, Types, And Functions
Defines Unix `platformRunFlags`, `NewContainer`, ID mapping parsers, namespace validation, `getNetNSPath`, GPU vendor/device helpers, CDI registry option, and `withCDIDeviceRequests`.

## Control Flow
Builds OCI spec opts from image or rootfs/config, unpacks image if needed, creates writable or userns-remapped snapshots, applies env/mounts/process/tty/privileged/net-host/seccomp/apparmor/cgroups/resources/devices/CDI/blockio/RDT/hostname/rlimits, records CNI extension metadata, resolves runtime options, and calls `client.NewContainer`.

## State And Persistence
Persists container metadata, snapshot metadata, unpacked layers, CNI extension metadata, and runtime options in containerd; reads host files for env/seccomp/apparmor/blockio/CDI and probes `/proc` for netns paths.

## Dependencies And Integration Points
Depends on containerd image/snapshot/diff/OCI packages, apparmor/seccomp contrib packages, goresctrl blockio, CDI libraries, OCI runtime spec, and platform defaults.

## Risks And Test Signals
Security-sensitive options can grant host devices, host networking, capabilities, or disabled cgroups. User namespace flags must be paired; CDI vendor detection only supports NVIDIA and AMD. Tests cover GPU helper behavior in `run_unix_test.go`. Source size reviewed: 593 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/cmd/ctr/commands/run/run_unix.go -->
