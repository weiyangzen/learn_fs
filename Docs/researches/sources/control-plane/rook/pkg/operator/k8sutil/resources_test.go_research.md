# sources/control-plane/rook/pkg/operator/k8sutil/resources_test.go

## Purpose
This file tests owner-reference and resource parsing utilities.

## Important APIs, Types, and Functions
`TestMergeResourceRequirements()` validates first-over-second semantics. `TestYamlToContainerResourceArray()` and `TestYamlToContainerResource()` validate YAML conversion. `TestValidateOwner()` checks namespace constraints. `TestValidateController()` checks same and conflicting controllers. `TestSetOwnerReference()` checks append and non-duplication behavior.

## Control Flow, State, and Persistence
Tests operate on in-memory Kubernetes objects and resource quantities. No fake client is required.

## Dependencies and Integration Points
The tests use Kubernetes core metadata/resource APIs and testify. They protect owner-reference invariants used for Kubernetes garbage collection.

## Risks
The YAML invalid data cases rely on duplicate malformed keys producing errors; more semantic invalid cases are not covered. Controller reference append duplication is not explicitly asserted. Owner comparison by group/kind/name rather than UID is indirectly accepted.

## Test Signals
High-value signals include cross-namespace owner rejection, cluster-scoped object rejection for namespaced owners, default controller validation, and resource request/limit fallback behavior.
