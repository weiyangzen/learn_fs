# sources/control-plane/csi-driver-nfs/charts/v4.2.0/csi-driver-nfs/values.yaml

## Purpose
This values file supplies defaults for the v4.2.0 NFS CSI chart, covering images, service accounts, RBAC, driver name, feature flags, kubelet directory, and controller/node pod settings.

## Important APIs, Types, and Functions
Defaults include nfsplugin `v4.2.0`, csi-provisioner `v3.3.0`, livenessprobe `v2.8.0`, node-driver-registrar `v2.6.2`, controller service account `csi-nfs-controller-sa`, driver name `nfs.csi.k8s.io`, kubelet dir `/var/lib/kubelet`, `enableFSGroupPolicy: true`, and `enableInlineVolume: false`.

## Control Flow, State, and Persistence
Values control rendering of service accounts/RBAC, controller and node Deployments/DaemonSets, image pull secrets, scheduling, log levels, health ports, and resources. There are no built-in storage class, snapshot, resizer, or external snapshot controller values in this chart version.

## Dependencies and Integration Points
The file is consumed by v4.2.0 templates and Kubernetes CSI sidecars. The defaults assume standard kubelet paths and registry.k8s.io images.

## Risks and Test Signals
Risks include service account naming mismatch when customizing values, no storage class examples, no expansion/snapshot support, and older sidecar versions. Signals are `helm template` with customized RBAC names, install smoke tests, PVC provisioning/deletion, node registration, and image pull validation.
