# sources/cloud-native/cri-o/internal/factory/container/namespaces_linux.go

## Purpose
Configures Linux OCI namespaces for a container based on pod sandbox namespace paths and CRI namespace options, including host network/PID, pod PID namespace, and target-container PID namespace.

## Important APIs, Types, And Functions
- `SpecAddNamespaces(sb SandboxIFace, targetCtr *oci.Container, serverConfig *config.Config) error` is the main Linux namespace mutator.
- `ConfigureGeneratorGivenNamespacePaths(managedNamespaces []*namespace.ManagedNamespace, g *generate.Generator) error` maps CRI-O namespace manager types to OCI namespace types and adds/replaces generator namespaces.

## Control Flow
The method first joins all non-empty sandbox-managed namespace paths into the OCI generator. It then inspects container security context namespace options. Host network removes the OCI network namespace. Host PID removes the PID namespace. Pod PID requires a valid sandbox PID namespace path and replaces the OCI PID namespace with it. Target PID requires a target container, resolves its PID, asks the namespace manager for a PID namespace from `/proc`, sets that path in the spec, and stores the managed namespace in `c.pidns`.

## State And Persistence
Mutates `generate.Generator.Config.Linux.Namespaces` and may store a managed PID namespace in the container object. The managed namespace can imply filesystem state in the namespace manager, but this file itself does not write persistent files.

## Dependencies And Integration Points
Depends on CRI API namespace modes, OCI runtime-spec namespace types, runtime-tools generator APIs, CRI-O namespace manager, sandbox namespace metadata, target OCI containers, and server config namespace manager. It is part of container creation before runtime handoff.

## Risks And Edge Cases
`ConfigureGeneratorGivenNamespacePaths` indexes a map of supported namespace types and errors on unknown types. Empty namespace paths are skipped. Pod PID mode errors if the sandbox was not similarly configured or has no valid infra PID namespace path. Target PID mode errors on nil target, PID lookup failure, namespace-manager failure, or generator update failure. The caller must later remove `c.pidns`.

## Test Signals
`namespaces_test.go` covers inherited sandbox namespaces, host-network removal, host-PID removal, pod PID namespace replacement, target PID namespace creation, and empty path skipping.
