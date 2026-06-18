# sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose

This template creates the `storage.k8s.io/v1` `CSIDriver` object for the NFS CSI driver. It advertises cluster-wide CSI driver capabilities under `.Values.driver.name`, which defaults to `nfs.csi.k8s.io`.

## APIs, control flow, and state

The rendered object sets `attachRequired: false`, telling Kubernetes that the driver does not need attach/detach controller operations before mounts. `volumeLifecycleModes` always includes `Persistent` and conditionally includes `Ephemeral` when `.Values.feature.enableInlineVolume` is true. When `.Values.feature.enableFSGroupPolicy` is true, `fsGroupPolicy: File` tells Kubernetes to apply file ownership behavior for mounted filesystems. The object stores declarative driver capability state in the Kubernetes API; it has no pod-local state or persistence.

## Dependencies and integration points

The `CSIDriver` object is consumed by kubelet, scheduler/storage control plane behavior, and CSI sidecars. It must match the `--drivername` argument used by both controller and node NFS plugin containers. Inline volume behavior must be coordinated with the driver's actual support and with workloads that use CSI ephemeral volumes.

## Risks and test signals

The main risk is capability drift: if the object advertises inline volumes or FSGroup behavior the driver/runtime cannot honor, workloads can fail at mount time or receive unexpected ownership. If the name differs from provisioned `StorageClass` drivers or container `--drivername`, Kubernetes treats them as different drivers. Test with `kubectl get csidriver`, provisioning a PVC through a matching `StorageClass`, pod mounts that exercise FSGroup, and a Helm render matrix toggling `enableInlineVolume` and `enableFSGroupPolicy`.
