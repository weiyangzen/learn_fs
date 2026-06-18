# sources/control-plane/csi-driver-nfs/charts/v4.7.0/csi-driver-nfs/values.yaml

## Purpose
Default configuration for the v4.7.0 CSI NFS Helm chart.

## Important APIs, Types, And Functions
Defines image repositories/tags, service-account names, RBAC naming, driver name and mount permissions, feature flags, kubelet directory, controller/node scheduling and resources, external snapshotter settings, image pull secrets, and example StorageClass parameters.

## Control Flow
Templates read these values to decide which objects render, which images run, what command flags are passed, and how pods are scheduled. v4.7.0 sets NFS plugin `v4.7.0`, csi-provisioner `v5.0.1`, csi-snapshotter and snapshot-controller `v8.0.1`, livenessprobe `v2.13.1`, and registrar `v2.11.1`.

## State And Persistence
Values are Helm release input. They become persisted Kubernetes object specs and influence persistent resources such as PVs, StorageClasses, CRDs, and RBAC.

## Dependencies And Integration Points
Couples every template in this chart. Key integrations include `driver.name` matching the `CSIDriver` and StorageClass, `kubeletDir` matching host kubelet layout, and snapshot flags controlling CRD/controller/RBAC emission.

## Risks And Edge Cases
Default snapshotter is disabled, StorageClass creation is disabled, and controller/node pods require privileged NFS mount capability. The example StorageClass lacks annotations in this version. Changing `driver.name` can break the v4.7.0 storageclass template because it hard-codes the provisioner.

## Test Signals
`helm template` across default and enabled-feature values, plus install smoke tests for provisioning, node registration, and optional snapshotting.
