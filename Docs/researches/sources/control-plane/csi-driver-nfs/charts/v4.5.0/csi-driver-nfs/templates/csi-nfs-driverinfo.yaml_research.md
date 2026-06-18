# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/templates/csi-nfs-driverinfo.yaml

## Purpose

This template renders the v4.5.0 `CSIDriver` object for the NFS CSI driver. It advertises the driver name and capabilities to Kubernetes storage components.

## APIs, control flow, and state

The object sets `attachRequired: false`, always advertises `Persistent` volume lifecycle support, conditionally advertises `Ephemeral` inline CSI volumes, and conditionally sets `fsGroupPolicy: File`. All conditionals are driven by `.Values.feature.enableInlineVolume` and `.Values.feature.enableFSGroupPolicy`. The persisted state is the Kubernetes `CSIDriver` API object; no pod-local state exists here.

## Dependencies and integration points

The object must match the `--drivername` passed to controller and node plugin containers and the `provisioner` value used by StorageClasses. Kubelet and storage admission behavior consume `attachRequired`, lifecycle modes, and FSGroup policy.

## Risks and test signals

Incorrect capability advertisement is the main risk. Enabling inline volumes or FSGroup policy without working runtime support can break workload mounts; changing the driver name creates a new identity from Kubernetes' perspective. Test `helm template`, `kubectl get csidriver -o yaml`, PVC provisioning, pod mounts with FSGroup, and optional inline CSI volume pods.
