# sources/control-plane/csi-driver-host-path/deploy/kubernetes-distributed/test-driver.yaml

## Purpose
This test-driver config describes the distributed hostpath deployment to Kubernetes external storage e2e. It uses an existing fast StorageClass and advertises topology and capacity behavior.

## Important APIs, Types, And Functions
The file sets `StorageClass.FromExistingClassName: csi-hostpath-fast`, `DriverInfo.Name: hostpath.csi.k8s.io`, minimum size `1Mi`, and capabilities for block, exec, multipods, node expansion, persistence, single-node volumes, topology, and capacity. It declares topology key `topology.hostpath.csi/node` and shared inline volumes.

## Control Flow
`deploy.sh` copies this file to `CSI_PROW_TEST_DRIVER` when requested and substitutes `capacity: true` with the actual cluster support detected for CSIStorageCapacity. The e2e framework then targets `csi-hostpath-fast` instead of creating a new class.

## State, Persistence, And Dependencies
The file is static test metadata, but its capacity line is deploy-time mutable. It depends on the fast StorageClass and distributed CSIDriver/DaemonSet being applied.

## Integration Points
It aligns with the driver node topology key, distributed capacity objects, and fast/slow StorageClass model.

## Risks
The `capacity` field must match real API support or tests will fail or skip incorrectly. Snapshot and controller expansion are not advertised here because the distributed deployment does not include those sidecars.

## Test Signals
Run e2e with the generated file and verify late binding, topology, capacity, block, inline, and node expansion cases match distributed deployment behavior.
