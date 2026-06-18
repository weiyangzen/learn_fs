# sources/control-plane/csi-driver-smb/test/external-e2e/testdriver.yaml

## Purpose
This YAML describes the SMB CSI driver to Kubernetes external storage e2e tests.

## Important APIs, Types, And Functions
It defines `ShortName: smb`, a `StorageClass.FromFile` path at `/tmp/csi/storageclass.yaml`, and `DriverInfo` for `test.csi.k8s.io`.

## Control Flow
There is no code flow. The external e2e binary reads this manifest to discover the driver name, storage class source, and capabilities.

## State, Persistence, And Dependencies
The file depends on `run.sh` having copied a valid StorageClass to `/tmp/csi/storageclass.yaml`. Capability flags advertise persistence, exec, multipods, RWX, fsGroup, controller expansion, volume mount group, and PVC data sources; node expansion is disabled.

## Integration Points
It integrates with Kubernetes external storage tests via `--storage.testdriver`.

## Risks And Test Signals
Incorrect capability flags can enable tests the driver cannot satisfy or skip needed coverage. Test signals come from external e2e cases selected by the capability matrix.
