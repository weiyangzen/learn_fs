# sources/control-plane/csi-driver-host-path/deploy/kubernetes-1.30-test/test-driver.yaml

## Purpose
This file describes the hostpath deployment to Kubernetes external storage e2e tests. It advertises which storage features the deployed driver supports so the test suite can select relevant test patterns.

## Important APIs, Types, And Functions
The YAML declares `StorageClass.FromName`, `SnapshotClass.FromName`, `DriverInfo.Name: hostpath.csi.k8s.io`, minimum size `1Mi`, and capabilities for block, controller expansion, exec, multipods, node expansion, persistence, single-node volumes, snapshot data sources, topology, and `FSResizeFromSourceNotSupported`. It also enables shared inline volumes.

## Control Flow
The deploy script may copy this file to `CSI_PROW_TEST_DRIVER` and append `ClientNodeName` based on the running plugin pod. The e2e framework reads it to create storage classes/snapshot classes by name and skip unsupported cases.

## State, Persistence, And Dependencies
The file itself is static test configuration. Its correctness depends on the deployed manifests actually enabling the advertised sidecars and driver flags.

## Integration Points
It integrates with Kubernetes Prow storage e2e, the deploy script, hostpath StorageClass/SnapshotClass resources, and the driver's controller and node capability responses.

## Risks
Over-advertising capabilities causes false test failures. Under-advertising skips coverage. The file still references Kubernetes 1.17 external storage test docs although it is used for newer deployment variants. Same-node constraints require deploy-time `ClientNodeName` injection.

## Test Signals
Run the external storage e2e suite with the copied file and verify selected tests match the manifest set, especially block, expansion, snapshot, topology, and inline volume cases.
