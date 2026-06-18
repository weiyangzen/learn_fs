# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/provision_spec.go

## Purpose
`provision_spec.go` builds the Kubernetes Job and Pod template used to run `rook ceph osd provision`. This is the prepare/provision half of OSD orchestration: it mounts host or PVC devices, injects OSD selection and store config through environment variables, applies placement/resources, and cleans up stale prepare Jobs.

## Important APIs, Types, and Functions
Key entry points are `Cluster.makeJob()`, `Cluster.provisionPodTemplateSpec()`, `Cluster.provisionOSDContainer()`, `Cluster.applyResourcesToAllContainers()`, `Cluster.deleteAllOrphanedPrepareJobs()`, `provisionJobName()`, and `provisionJobLabels()`. `makeJob()` wraps the pod template in a `batch.Job`, labels PVC-backed jobs with `OSDOverPVCLabelKey` and `CephDeviceSetLabelKey`, applies Rook/Ceph version labels, owner refs, and prepare resources.

## Control Flow, State, and Persistence
Provisioning begins by generating a pod template with a copied Rook binary, projected Ceph config volumes, `/dev`, `/run/udev`, and Ceph secrets. Non-PVC jobs mount host `/` as `rootfs` and pin the pod to the target hostname. PVC jobs add PVC bridge volumes, optional metadata/WAL bridge init containers, encryption volumes, and KMS mounts/env vars when configured. `provisionOSDContainer()` selects exactly one data-device source by priority: explicit devices, device filter, device path filter, then all devices. It serializes configured devices to JSON for `ROOK_DATA_DEVICES` and adds migration replacement OSD IDs when relevant.

## Dependencies and Integration Points
The file depends on CephCluster storage/security specs, OSD config env helpers from nearby files, KMS helpers, monitor secret volumes, controller pod volume utilities, `k8sutil` labels/owner refs, and Kubernetes Job/Pod APIs. Its output is consumed by the status workflow in `status.go`: prepare pods report into status ConfigMaps that trigger OSD deployment creation.

## Risks
Prepare pods are privileged and mount `/dev`; security context changes must preserve ceph-volume and block-device access. Device-selection priority is behaviorally important and easy to alter accidentally. PVC encryption has provider-specific volume and env handling for Vault and KMIP. `applyResourcesToAllContainers()` overrides init and main container resources after pod generation, so callers expecting fine-grained resources could be surprised. Orphan cleanup only deletes Jobs whose pod template has a hostname selector missing from current node labels.

## Test Signals
Covered indirectly by `spec_test.go` and `osd_test.go`: prepare pod command/args, scheduler propagation, storage config env vars, prepare resources, PVC/non-PVC placement merging, host network DNS policy, and orphaned prepare Job deletion.
