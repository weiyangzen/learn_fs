# sources/control-plane/csi-driver-nfs/charts/v4.6.0/csi-driver-nfs/values.yaml

## Purpose

This file defines the default values for the v4.6.0 NFS CSI driver Helm chart. It configures image repositories/tags, RBAC and service accounts, driver capabilities, kubelet paths, controller and node scheduling/resources, snapshot-controller defaults, CRD rendering, and image pull secrets.

## APIs, control flow, and state

Compared with v4.5.0, it adds `image.baseRepo: registry.k8s.io` and advances images to NFS plugin `v4.6.0`, provisioner `v4.0.0`, snapshotter/snapshot-controller `v6.3.3`, liveness probe `v2.12.0`, and registrar `v2.10.0`. The base repo is used by templates only when a component repository starts with `/`; default repositories remain full image names. Snapshot-controller remains disabled by default while CRD creation remains true under the snapshotter block, meaning CRDs render only if both toggles are true.

Controller and node defaults preserve host-network DNS policy, liveness ports, resources, critical priority, tolerations, `kubeletDir`, driver name, FSGroup policy, inline-volume disabled, and optional host mount option propagation disabled. Values are persisted through Helm release state and rendered Kubernetes resources.

## Dependencies and integration points

The new base-repo setting integrates with v4.6.0 image conditionals in controller, node, and snapshot-controller templates. Other values drive `CSIDriver`, RBAC, CRD, service-account, deployment, and DaemonSet rendering.

## Risks and test signals

Image mirror behavior is easy to misconfigure because only slash-prefixed repositories use `baseRepo`. Upgrading sidecars may change Kubernetes compatibility expectations. Test default render, slash-prefixed mirror render, image pull behavior, upgrade from v4.5.0, snapshot enablement, custom service accounts, custom `kubeletDir`, and host mount option propagation.
