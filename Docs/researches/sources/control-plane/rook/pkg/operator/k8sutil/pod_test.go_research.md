# sources/control-plane/rook/pkg/operator/k8sutil/pod_test.go

## Purpose
This file validates selected pod utilities in `pod.go`.

## Important APIs, Types, and Functions
`TestGetContainerByName()` covers missing and found containers and verifies the returned pointer mutates the source slice element. `TestGetPodPhaseMap()` groups pod names by phase. `TestAddUnreachableNodeToleration()` checks default, env override, replacement positions, and invalid env fallback. `TestPodSpecPlacement()` checks anti-affinity counts after applying placement. `TestIsMonScheduled()` checks pod scheduling via label selectors.

## Control Flow, State, and Persistence
Tests use fake clientsets from `operator/test`, local pod specs, and `t.Setenv()` for toleration seconds. Kubernetes state is in-memory only.

## Dependencies and Integration Points
The tests use Rook Ceph placement, pod anti-affinity APIs, Kubernetes fake clients, and testify. They protect operator scheduling behavior for mons and other pods.

## Risks
The anti-affinity helper assumes initialized affinity state, but the tests rely on `Placement.ApplyToPodSpec()` to set that up. `ForceDeletePodIfStuck()`, duplicate env removal, running-pod environment lookup, and pod label counting are not covered here.

## Test Signals
Useful signals include idempotent unreachable toleration replacement, invalid env fallback to five seconds, pointer semantics for container lookup, and first-pod scheduling behavior in `IsPodScheduled()`.
