# sources/cloud-native/containerd/internal/cri/annotations/annotations.go

## Purpose

`annotations.go` centralizes CRI-related OCI annotation keys and builds the default annotation spec options for sandbox and workload containers.

## Important APIs, Types, and Functions

- Constants include container type values, sandbox/container metadata keys, sandbox CPU/memory keys, sandbox log/image keys, untrusted workload, runtime handler fallback, and Windows HostProcess annotation.
- `DefaultCRIAnnotations` returns `oci.SpecOpts` that add sandbox ID, namespace, UID, name, container type, and either sandbox log/image annotations or container name/image annotations.

## Control Flow

`DefaultCRIAnnotations` starts with common sandbox metadata, selects `sandbox` or `container` type based on the boolean argument, appends sandbox-specific or container-specific annotations, and appends the final container type annotation.

## State and Persistence Behavior

The file does not persist state itself. Its constants become OCI spec annotations written into runtime specs and consumed by runtimes, shims, and integration tests.

## Dependencies and Integration Points

It depends on CRI runtime API types, containerd CRI spec option helpers, and OCI spec option plumbing. The constants integrate with Kata, kubelet/CRI metadata expectations, HostProcess handling, and runtime handler fallback compatibility.

## Risks and Edge Cases

Annotation key changes are compatibility-sensitive because external runtimes and tests may depend on exact names. The `RuntimeHandler` annotation is deprecated and should remain only as a fallback for older CRI clients until removal.

## Test Signals

No direct unit test appears in this subset. Coverage is indirect through CRI spec generation, sandbox/container lifecycle tests, HostProcess tests, and runtime-handler behavior.
