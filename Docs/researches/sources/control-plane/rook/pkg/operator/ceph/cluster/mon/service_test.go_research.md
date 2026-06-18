# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/service_test.go

## Purpose
This test file validates monitor service creation and ClusterIP preservation/recovery behavior.

## Important APIs, Types, And Functions
`TestCreateService` constructs a monitor `Cluster` with a fake Kubernetes client and calls `c.createService(m)` repeatedly. It inspects the returned service and deletes the fake service to simulate disaster recovery.

## Control Flow And State
The first call creates a monitor service without `PublicIP`, so the fake service has an empty ClusterIP. The second call sets `m.PublicIP` but leaves the service present, verifying the existing service's ClusterIP is not changed. The test then deletes the service and calls `createService` again, verifying `Spec.ClusterIP` is set to the expected monitor public IP when recreating a missing service.

## Dependencies And Integration Points
The test depends on Rook fake Kubernetes clientsets, monitor cluster construction, and the admin test cluster info. It validates behavior at the Kubernetes Service API object layer rather than through higher-level monitor startup.

## Risks And Test Signals
The test directly covers the disaster recovery condition documented in `service.go`. It does not assert labels/selectors/ports, so port selection and service identity rely on broader monitor tests or Kubernetes helper tests elsewhere.
