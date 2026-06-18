# sources/control-plane/csi-driver-nfs/charts/v4.8.0/csi-driver-nfs/values.yaml

## Purpose
Default configuration for the v4.8.0 CSI NFS Helm chart.

## Important APIs, Types, And Functions
Configures chart images, service accounts, RBAC, driver name, feature flags, kubelet directory, controller and node pod defaults, external snapshotter, image pull secrets, and example StorageClass settings.

## Control Flow
Templates consume these values for rendering Kubernetes objects and command arguments. v4.8.0 updates NFS plugin image to `v4.8.0` and csi-provisioner to `v5.0.2` while keeping snapshotter, liveness, registrar, and snapshot-controller tags aligned with v4.7.0 defaults.

## State And Persistence
Values are installed into Helm release metadata and rendered Kubernetes object specs. Resource limits, feature flags, and StorageClass parameters become persistent cluster configuration.

## Dependencies And Integration Points
Controls every chart template. Important cross-file links are `driver.name`, `kubeletDir`, snapshotter flags, controller/node liveness ports, and StorageClass annotations introduced in the example comments.

## Risks And Edge Cases
Snapshotter and StorageClass creation remain disabled by default. Controller and node NFS containers require privileged operation. The default-class annotation is commented and must be enabled explicitly.

## Test Signals
`helm lint`, rendered YAML diffs from v4.7.0, install smoke tests, and provisioning/snapshotting tests under enabled feature flags.
