# sources/cloud-native/cri-o/internal/factory/container/sandbox.go

## Purpose
Defines the narrow sandbox interface needed by the container factory so factory code can consume sandbox information without importing the full sandbox implementation package.

## Important APIs, Types, And Functions
- `SandboxIFace` exposes log directory, annotations, ID/name, resolv path, IPs, managed namespace paths, PID namespace path, and CRI namespace options.

## Control Flow
This file declares an interface only. Runtime behavior is supplied by concrete sandbox objects implementing these methods.

## State And Persistence
No state is held or persisted. Interface methods expose state from sandbox implementations.

## Dependencies And Integration Points
Uses CRI namespace option types and CRI-O `internal/lib/namespace.ManagedNamespace`. The interface is consumed by annotation setup, namespace setup, and other factory operations that need pod sandbox metadata.

## Risks And Edge Cases
Because it is intentionally narrow, future factory methods needing more sandbox data must extend this interface. Implementations must preserve semantics such as empty PID namespace path meaning no infra namespace is available.

## Test Signals
Indirectly tested wherever sandbox builder or sandbox instances are passed to factory methods in `container_test.go` and `namespaces_test.go`.
