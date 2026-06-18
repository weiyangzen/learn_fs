# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose

This v4.6.0 template renders the `CSIDriver` object for the NFS CSI driver, declaring attach and lifecycle capabilities to Kubernetes.

## APIs, control flow, and state

The rendered object sets `attachRequired: false`, includes `Persistent` lifecycle mode, optionally includes `Ephemeral`, and optionally sets `fsGroupPolicy: File`. The file is unchanged from v4.4.0/v4.5.0 except for the values it reads at render time. The object persists cluster-level driver capability state in the Kubernetes API.

## Dependencies and integration points

The driver name must match controller/node `--drivername` and StorageClass provisioner names. Kubernetes storage components and kubelet consume the attach, lifecycle, and FSGroup declarations when admitting and mounting workloads.

## Risks and test signals

The risk is mismatch between advertised and actual driver behavior. Test a rendered install with default and custom driver names, PVC provisioning, pod mount with FSGroup, and optional inline CSI volumes when enabled. Also verify upgrades do not delete/recreate the `CSIDriver` unexpectedly when only feature toggles change.
