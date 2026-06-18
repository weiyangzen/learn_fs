# sources/control-plane/csi-driver-nfs/charts/v4.5.0/csi-driver-nfs/values.yaml

## Purpose

This is the default values contract for chart v4.5.0. It configures images, identities, RBAC, driver features, scheduling, resources, snapshot-controller behavior, CRD rendering, and image pull secrets.

## APIs, control flow, and state

Compared with v4.4.0, image tags advance to NFS plugin `v4.5.0`, provisioner `v3.6.1`, snapshotter/snapshot-controller `v6.3.1`, liveness probe `v2.11.0`, and registrar `v2.9.0`. It adds `.Values.serviceAccount.node`, `.Values.feature.propagateHostMountOptions`, and `.Values.externalSnapshotter.customResourceDefinitions.enabled`. It changes `.Values.externalSnapshotter.enabled` default from true to false, meaning the snapshot-controller and CRDs are not installed by default.

The controller and node defaults otherwise preserve critical priority, host-network DNS policy, liveness ports, Linux scheduling, tolerations, resource requests/limits, `kubeletDir`, FSGroup policy, and driver name. Values become persisted only through rendered Kubernetes resources and Helm release state.

## Dependencies and integration points

The new node service account value integrates with the v4.5.0 node DaemonSet template. `propagateHostMountOptions` integrates with node hostPath mounts for `/etc/nfsmount.conf`. The CRD toggle integrates with the snapshot CRD template and lets operators rely on separately managed CRDs.

## Risks and test signals

The default disabling of external snapshotter/CRDs changes install behavior from v4.4.0 and can break users expecting snapshots immediately after install. Host mount option propagation can create node-specific behavior. Test default `helm template`, upgrade from v4.4.0, explicit snapshot enablement, custom node service accounts, host mount option propagation, and private registry image pull secrets.
