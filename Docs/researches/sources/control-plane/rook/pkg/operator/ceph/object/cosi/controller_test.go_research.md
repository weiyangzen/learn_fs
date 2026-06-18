# sources/control-plane/rook/pkg/operator/ceph/object/cosi/controller_test.go

## Purpose
`cosi/controller_test.go` verifies deployment-strategy behavior for the Ceph COSI driver controller.

## Important APIs, Types, and Functions
`TestCephCOSIDriverController` sets `POD_NAMESPACE`, builds fake clients and schemes, and runs the reconciler with combinations of CephCOSIDriver CRs and CephObjectStore CRs. It checks no-CR default behavior, explicit `Never`, `Always`, `Auto`, custom images, namespace validation, and multiple CR rejection.

## Control Flow, State, and Persistence
The tests use in-memory fake clients and inspect whether an `apps/v1.Deployment` exists after reconciliation. Auto mode without object stores is expected to requeue and not create a Deployment; Auto with an object store creates one. Always creates a Deployment even without object stores. Never avoids or deletes deployment state.

## Dependencies and Integration Points
The suite depends on Rook API schemes, Kubernetes apps scheme registration, fake controller-runtime clients, fake event recorders, and executor/test context scaffolding. It validates controller behavior and some deployment spec fields, such as the custom driver image.

## Risks and Test Signals
Signals are clear for strategy selection and namespace guardrails. Gaps include deployment update semantics, owner references, labels, placement/resources, sidecar image override, service account/volume details, and actual watch behavior from CephObjectStore events.
