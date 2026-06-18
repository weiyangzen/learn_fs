# sources/cloud-native/cri-o/internal/lib/container_server_freebsd.go

## Purpose
Provides FreeBSD-specific namespace path restoration logic for container server sandbox loading.

## Important APIs, Types, And Functions
- `configNsPath(spec *rspec.Spec, nsType rspec.LinuxNamespaceType) (string, error)` returns the sandbox ID for network namespaces when the sandbox is not host-networked.

## Control Flow
If the requested namespace type is `NetworkNamespace` and the spec annotation does not indicate host network, the function returns `annotations.SandboxID`. Otherwise it returns a missing namespace error.

## State And Persistence
No state is changed. The returned path-like value is interpreted by FreeBSD code as the jail name for the infra container owning pod vnet.

## Dependencies And Integration Points
Used by `LoadSandbox` when joining namespaces. Integrates runtime-spec namespace types with FreeBSD jail semantics and CRI-O annotations.

## Risks And Edge Cases
Only network namespace is supported. It ignores actual `spec.Linux.Namespaces` entries and relies on annotations. Host-networked sandboxes report missing namespace.

## Test Signals
No FreeBSD-specific tests in this subset; common `LoadSandbox` tests primarily exercise Linux behavior.
