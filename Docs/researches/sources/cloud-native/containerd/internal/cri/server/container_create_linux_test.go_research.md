# sources/cloud-native/containerd/internal/cri/server/container_create_linux_test.go

## Purpose
This Linux-focused test suite validates CRI container OCI spec generation for security, namespaces, mounts, process identity, devices, CDI injection, cgroup behavior, and Linux-specific compatibility rules. It shares `getCreateContainerTestData` with generic create tests but extends it with Linux `SecurityContext`, resource, and namespace assertions.

## Important APIs, Types, and Functions
Key tests include `TestContainerCapabilities`, `TestContainerSpecTty`, `TestContainerSpecDefaultPath`, `TestContainerSpecReadonlyRootfs`, `TestContainerSpecWithExtraMounts`, `TestContainerAndSandboxPrivileged`, `TestPrivilegedBindMount`, `TestCgroupNamespace`, `TestMountPropagation`, `TestPidNamespace`, `TestUserNamespace`, `TestMaskedAndReadonlyPaths`, `TestHostname`, `TestProcessUser`, `TestNonRootUserAndDevices`, `TestPrivilegedDevices`, `TestBaseOCISpec`, `TestCDIInjections`, and `TestUserNamespaceWithHostNetwork`. It exercises `buildContainerSpec`, `platformSpecOpts`, `opts.WithMounts`, `customopts.WithCDI`, and OCI spec structures.

## Control Flow, State, and Persistence
The tests build synthetic CRI container/sandbox/image configs, invoke spec construction, and inspect the resulting in-memory OCI spec. Temporary files are used for `/etc/passwd`, `/etc/group`, and CDI YAML specs; no containerd runtime is started. Fake OS hooks simulate mount lookup and hostname behavior. User namespace tests also ensure sandbox and container namespace configs must match.

## Dependencies and Integration Points
Coverage spans Linux capability sets, SELinux labels, cgroup v1/v2 namespace selection, mount propagation validation, host/pod/container PID namespace wiring, supplemental group policies, base runtime specs, CDI registry configuration, device ownership, and privileged runtime toggles. It ties CRI API fields to OCI runtime-spec output.

## Risks and Test Signals
Primary risks are privilege escalation, invalid namespace combinations, host mount propagation misuse, incorrect user/group merging, CDI injection drift, device ownership regressions, and host-network plus userns `/sys` mount failures. Strong signals are exact spec field comparisons, expected errors for invalid namespace/idmap inputs, and platform-gated cgroup assertions.
