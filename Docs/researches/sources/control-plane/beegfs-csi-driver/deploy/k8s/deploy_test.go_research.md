<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/deploy_test.go -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/deploy_test.go

## Purpose
`deploy_test.go` protects the embedded deployment-manifest contract used by the operator and direct deployments.

## Important APIs, Types, and Functions
Tests include `TestGetRBAC()`, `TestGetControllerServiceStatefulSet()`, `TestGetCSIDriver()`, and `TestGetNodeServiceDaemonSet()`. Helpers `testForKeysInContainerArgs()` and `testForResourceNamesInPodVolumes()` validate that config, connection auth, and TLS keys/resource names appear in container args and pod volumes.

## Control Flow
Each test calls the accessor from `deploy.go`, fails on unmarshal errors, and then scans returned Kubernetes objects for expected types or expected names. Container checks ensure operator-sensitive container names exist in controller and node pod specs.

## State and Persistence
The tests create in-memory Kubernetes API objects only. They persist no files or cluster state.

## Dependencies and Integration Points
The file depends on Go testing, Kubernetes API types, and a blank Ginkgo import so normal `go test` tolerates Ginkgo flags. It validates assumptions relied on by operator code that mutates embedded manifests.

## Risks
The tests check presence but not full semantic correctness of manifests. They do not verify resource quantities, security contexts, host paths, sidecar image versions, or all RBAC permissions. String containment in args could pass for stale or commented-like values if args are malformed.

## Test Signals
These are themselves unit-test signals. They should run in normal `make test` and fail if core names, keys, volumes, or object typing change without corresponding operator refactors.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/deploy_test.go -->
