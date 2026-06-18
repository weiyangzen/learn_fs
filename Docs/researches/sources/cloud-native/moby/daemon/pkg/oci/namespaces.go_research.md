<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/namespaces.go -->
# sources/cloud-native/moby/daemon/pkg/oci/namespaces.go

## Purpose
Provides small helpers for editing and querying namespace entries in an OCI runtime spec.

## Important APIs, Types, And Functions
`RemoveNamespace(*specs.Spec, specs.LinuxNamespaceType)` removes the first namespace of a requested type if `s.Linux` exists. `NamespacePath(*specs.Spec, specs.LinuxNamespaceType)` returns the first matching namespace path and a boolean.

## Control Flow
Both functions linearly scan `s.Linux.Namespaces`. Removal rewrites the slice with `append(slice[:i], slice[i+1:]...)` and stops after the first match.

## State, Dependencies, And Integration Points
They mutate only the provided spec in memory and depend on `github.com/opencontainers/runtime-spec/specs-go`. Plugin spec generation uses `RemoveNamespace` when plugins request host network, PID, or IPC namespaces.

## Risks And Test Signals
`NamespacePath` assumes `s.Linux` is non-nil and would panic otherwise, unlike `RemoveNamespace`. No direct tests are in this subset; integration coverage comes through plugin spec creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/oci/namespaces.go -->
