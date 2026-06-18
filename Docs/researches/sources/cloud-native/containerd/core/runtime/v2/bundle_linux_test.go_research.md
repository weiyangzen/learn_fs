# sources/cloud-native/containerd/core/runtime/v2/bundle_linux_test.go

## Purpose
Validates Linux-specific bundle permission and GID remapping behavior.

## APIs, Flow, State, Dependencies, Risks, And Tests
`TestNewBundle` runs as root, creates temporary root/state directories, marshals OCI specs with and without Linux GID mappings, calls `NewBundle`, and asserts directory mode plus `syscall.Stat_t.Gid`. `TestRemappedGID` marshals several minimal OCI specs and verifies `remappedGID` returns zero for no mapping and the expected host GID for container ID 0.

The tests create temporary bundle/work filesystem state and remove it through test temp cleanup. They depend on `testutil.RequiresRoot`, typeurl, OCI/specs structs, and `testify` assertions.

The important signal is that bundle directory permissions are stable for both ordinary and userns-remapped containers. Risks covered include missing Linux sections, empty mappings, mappings for non-root container IDs, and invalid ownership expectations. Gaps include negative tests for malformed spec JSON and chown/chmod failure injection.
