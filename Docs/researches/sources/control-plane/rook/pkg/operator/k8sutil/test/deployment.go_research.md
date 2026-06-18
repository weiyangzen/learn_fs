# sources/control-plane/rook/pkg/operator/k8sutil/test/deployment.go

## Purpose
This test helper provides a stub for deployment update-and-wait behavior used by Rook unit tests.

## Important APIs, Types, and Functions
`UpdateDeploymentAndWaitStub()` returns a function matching the production update signature plus a pointer to a slice of deployments passed to it. `DeploymentNamesUpdated()` maps that slice to deployment names. `ClearDeploymentsUpdated()` resets it.

## Control Flow, State, and Persistence
The stub appends received deployment pointers to a captured slice and always returns nil. State is held in the returned slice pointer and is controlled by the test.

## Dependencies and Integration Points
It depends on Rook `clusterd.Context`, Ceph `client.ClusterInfo`, and Kubernetes apps/v1 deployments so it can be assigned where production `UpdateDeploymentAndWait` is expected.

## Risks
The stub stores pointers without deep-copying, despite the comment describing a copy. Later mutations to deployment objects can affect recorded values. It does not simulate errors, resource versions, rollout waits, or upgrade checks.

## Test Signals
No direct tests are mapped. Downstream unit tests can assert which deployments were requested for update and clear the recorder between phases.
