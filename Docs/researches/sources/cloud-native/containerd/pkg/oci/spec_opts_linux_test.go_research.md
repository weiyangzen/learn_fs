# sources/cloud-native/containerd/pkg/oci/spec_opts_linux_test.go

Purpose: Linux-specific tests for capabilities and device helpers.

Important APIs/types/functions: `TestSetCaps`, `TestAddCaps`, and `TestDropCaps` validate bounding/effective/permitted/inheritable behavior. `TestGetDevices` creates temporary character device nodes and validates recursive discovery and container paths. `TestWithLinuxDeviceFollowSymlinks` verifies symlink resolution behavior for device specs.

Control flow: tests construct specs, apply options, and compare capability lists or device entries. Device tests require mknod-capable environments and skip where unsupported.

State/persistence: temporary filesystem nodes only.

Dependencies/integration: uses Linux device syscalls, runtime-spec types, and package helpers.

Risks: device tests may be skipped or fail in restricted CI without privileges. Capability ordering and host cap availability can vary.

Test signals: protects cgroup device rule generation, recursive device path handling, symlink-following option semantics, and capability mutation invariants.
