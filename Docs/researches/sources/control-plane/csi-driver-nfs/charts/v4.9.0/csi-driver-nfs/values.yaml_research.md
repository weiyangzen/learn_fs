# sources/control-plane/csi-driver-nfs/charts/v4.9.0/csi-driver-nfs/values.yaml

## Purpose
Default configuration for the v4.9.0 CSI NFS Helm chart.

## Important APIs, Types, And Functions
Defines image tags, service-account/RBAC defaults, driver name, mount permissions, feature flags, kubelet directory, controller and node defaults, snapshotter defaults, image pull secrets, and commented StorageClass examples.

## Control Flow
Templates consume these values to generate Kubernetes objects and plugin/sidecar command flags. v4.9.0 sets NFS plugin image `v4.9.0`, csi-provisioner `v5.0.2`, snapshotter/controller `v8.0.1`, livenessprobe `v2.13.1`, and registrar `v2.11.1`.

## State And Persistence
Values become Helm release metadata and rendered object specs. They define persistent cluster configuration for RBAC, CRDs if enabled, driver metadata, and optional StorageClass settings.

## Dependencies And Integration Points
Links all v4.9.0 templates. Notable integrations include `driver.name` now controlling the StorageClass provisioner, controller affinity flags, `kubeletDir` host paths, and optional snapshot controller/CRD flags.

## Risks And Edge Cases
Snapshotter and StorageClass remain disabled by default. Privileged NFS pods require permissive node policy. Upgrades from v4.8.0 should test control-plane scheduling and StorageClass provisioner behavior if custom driver names are used.

## Test Signals
`helm lint`, render diff from v4.8.0, install smoke tests for provisioning, scheduling with control-plane flags, node registration, and optional snapshots.
