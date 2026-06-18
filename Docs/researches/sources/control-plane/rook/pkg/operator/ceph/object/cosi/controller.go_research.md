# sources/control-plane/rook/pkg/operator/ceph/object/cosi/controller.go

## Purpose
`cosi/controller.go` reconciles the experimental Ceph COSI driver deployment. It enables, disables, or waits to deploy the driver based on `CephCOSIDriver.Spec.DeploymentStrategy` and the presence of CephObjectStores.

## Important APIs, Types, and Functions
`Add()` registers a controller for `CephCOSIDriver` and also watches `CephObjectStore` events. `ReconcileCephCOSIDriver.reconcile()` enforces that at most one CephCOSIDriver CR exists, defaults deployment strategy to `Never`, deletes the driver deployment when disabled, requires the CR namespace to match the operator pod namespace, waits for object stores in `Auto` mode, and calls `startCephCOSIDriver()`. `startCephCOSIDriver()` creates the Deployment from `createCephCOSIDriverDeployment()` and updates it on `AlreadyExists`.

## Control Flow, State, and Persistence
The reconciler lists all CephCOSIDriver CRs instead of using only the request key. When disabled it deletes the Deployment named by the request. When enabled it persists a single Kubernetes Deployment in the operator namespace. Auto mode returns a timed requeue until at least one CephObjectStore exists.

## Dependencies and Integration Points
It integrates controller-runtime, Rook COSI CRDs, CephObjectStore events, Kubernetes Deployments, operator pod namespace environment, event recording, and reporting. Deployment shape is delegated to `spec.go`.

## Risks and Test Signals
Risks include singleton enforcement across namespaces, delete path using request namespaced name rather than discovered CR identity, update without resource-version merge semantics, and namespace dependence on `POD_NAMESPACE`. Tests cover default disabled behavior, Never/Always/Auto strategies, custom image, custom namespace rejection, object-store-triggered Auto deployment, and multiple CR errors.
