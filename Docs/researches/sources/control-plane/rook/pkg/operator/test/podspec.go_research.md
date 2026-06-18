# sources/control-plane/rook/pkg/operator/test/podspec.go

## Purpose
`podspec.go` builds a test wrapper around Kubernetes `PodSpec` objects for common Rook pod-spec assertions.

## Important APIs, Types, and Functions
`PodSpecTester` stores `testing.T` and a pod spec pointer. `PodTemplateSpecTester.Spec()` creates a pod-spec tester from a template. `NewPodSpecTester()` constructs one directly. `AssertVolumesAndMountsMatch()` checks that all container mounts have corresponding volumes and all volumes are used. `RunFullSuite()` also delegates to container assertions. `allContainers()` concatenates init and normal containers.

## Control Flow, State, and Persistence
The helpers are in-memory assertion wrappers. `allContainers()` uses `append(p.InitContainers, p.Containers...)`, which can reuse the init-container backing array.

## Dependencies and Integration Points
It depends on Kubernetes pod spec types and the local volume/container test helpers. It is part of the operator test library used by daemon/deployment spec tests.

## Risks
Because full-suite checks require every volume to be mounted somewhere, shared optional volumes must be included carefully. Resource expectations apply to all containers through `ContainersTester`.

## Test Signals
No direct tests are mapped for this file. It is exercised indirectly by downstream operator pod-template spec tests.
