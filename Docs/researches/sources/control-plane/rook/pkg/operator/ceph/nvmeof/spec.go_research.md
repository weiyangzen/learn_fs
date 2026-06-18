<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/spec.go -->
# sources/control-plane/rook/pkg/operator/ceph/nvmeof/spec.go

## Purpose
This file generates Kubernetes Services, Deployments, init containers, daemon containers, labels, ports, placement defaults, and volumes for Ceph NVMe-oF gateway instances.

## Important APIs and control flow
`getPorts` resolves default or CR-specified IO, gateway, monitor, and discovery ports. `generateCephNVMeOFService` creates a per-instance Service exposing all four ports and uses headless service mode for host networking. `createCephNVMeOFService` creates the Service and treats AlreadyExists as success. `makeDeployment` validates reconciler state, builds a one-replica Deployment with generated Ceph config volume, admin keyring Secret, gateway ConfigMap volume, init container, privileged daemon container, host network/Multus settings, default and user placement, stable DNS hostname when valid, service account `rook-ceph-nvmeof`, labels, annotations, version labels, and config hash annotation. `getDefaultNVMeOFPlacement` adds topology spread by hostname. `createCephConfigInitContainer` embeds `connectionconfig.sh`, passes admin Ceph flags, sets gateway/pool/group/POD_IP env vars, mounts admin keyring, Ceph config, and config map, and runs privileged with SYS_ADMIN and NET_RAW dropped. `daemonContainer` resolves the image from CR or Ceph config, sets `CEPH_ARGS`, exposes ports, runs privileged, configures liveness probes, and mounts generated Ceph config. Helper functions provide default probes, labels, instance names, image lookup, gateway ConfigMap volume, and admin keyring volume/mount.

## State and persistence
State is Kubernetes resource spec plus generated files at pod runtime. Admin keyring is read from Secret `rook-ceph-admin-keyring`; generated Ceph files and rendered `nvmeof.conf` live in pod volumes. Deployment annotations store config hash for rollouts when Rook owns the ConfigMap.

## Dependencies and integration points
The file depends on embedded script support, Rook controller helpers for labels/probes/placement/Multus/version labels, Ceph config helpers for image lookup and default flags, Kubernetes validation for hostnames, and CephNVMeOFGateway CRD fields for ports, resources, placement, annotations, labels, image, and probes.

## Risks and test signals
Both init and daemon containers are privileged with SYS_ADMIN, increasing security sensitivity. Service creation does not update existing Services, so port changes may need manual recreation. If `spec.image` is empty and Ceph config lacks `mgr/cephadm/container_image_nvmeof`, deployment generation fails. Custom ConfigMap refs have empty config hash, so pod rollout is not automatic on config change. Tests for this file are mainly in `controller_test.go`, which verifies config map generation and controller resource lifecycle, but detailed deployment spec coverage appears limited in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/operator/ceph/nvmeof/spec.go -->
