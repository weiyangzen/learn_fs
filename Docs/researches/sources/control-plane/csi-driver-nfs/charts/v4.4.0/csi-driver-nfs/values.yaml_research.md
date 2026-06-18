# sources/control-plane/csi-driver-nfs/charts/v4.4.0/csi-driver-nfs/values.yaml

## Purpose

This file is the default configuration contract for the v4.4.0 NFS CSI Helm chart. It selects image tags, service-account and RBAC names, driver capabilities, kubelet paths, controller/node scheduling, resources, snapshot-controller behavior, and image pull secrets.

## APIs, control flow, and state

The values feed every template in this chart. Image defaults point to `registry.k8s.io/sig-storage/nfsplugin:v4.4.0`, `csi-provisioner:v3.5.0`, `csi-snapshotter:v6.2.2`, `livenessprobe:v2.10.0`, `csi-node-driver-registrar:v2.8.0`, and `snapshot-controller:v6.2.2`. The driver defaults to `nfs.csi.k8s.io`, `mountPermissions: 0`, FSGroup policy enabled, inline volumes disabled, and `kubeletDir: /var/lib/kubelet`.

Controller defaults include one replica, `Recreate`, host-network DNS policy, control-plane tolerations, `system-cluster-critical`, liveness port `29652`, log level `5`, `/tmp` working mounts, and delete-on-delete behavior. Node defaults include liveness port `29653`, `maxUnavailable: 1`, broad toleration, and critical priority. `externalSnapshotter.enabled` defaults to true in v4.4.0.

## Dependencies and integration points

These values integrate with Helm template functions, Kubernetes scheduling, image registry access, kubelet host paths, and snapshot CRD/RBAC rendering. They are not persisted directly except through rendered Kubernetes resources and any Helm release state.

## Risks and test signals

The default external snapshot-controller and CRD installation can conflict with platform-managed snapshot infrastructure. The node service account is not configurable in v4.4.0 values even though service-account creation creates a node account in later chart versions. Test signals include `helm template` with defaults, custom image tags, disabled RBAC/service accounts, custom `kubeletDir`, and toggles for `enableFSGroupPolicy`, `enableInlineVolume`, and `externalSnapshotter.enabled`.
