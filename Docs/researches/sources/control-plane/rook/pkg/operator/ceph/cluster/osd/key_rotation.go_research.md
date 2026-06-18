# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/key_rotation.go

## Purpose
This file reconciles Kubernetes CronJobs that periodically rotate encryption keys for encrypted PVC-backed OSDs. It builds the rotation container, pod template, CronJob object, placement rules, and cleanup behavior when key rotation is disabled.

## Important APIs, Types, and Functions
`keyRotationCronJobName()` formats stable per-OSD CronJob names. `applyKeyRotationPlacement()` removes topology spread constraints and pod anti-affinity, then installs required pod affinity matching the target OSD labels on the hostname topology key. This forces the rotation job onto the same node as the OSD pod.

`getKeyRotationContainer()` builds a privileged root container using the operator image (`c.rookVersion`) with args `key-management rotate-key <pvc> <devices...>`, debug logging, Ceph version, KMS env vars, ceph-volume config env vars, env-from overrides, resources, and security context dropping `NET_RAW`. `getKeyRotationPodTemplateSpec()` mounts `/dev`, `/run/udev`, and the OSD bridge host path under the cluster data dir; adds block, metadata, and wal devices when present; adds Vault TLS volumes when configured; applies host networking or Multus; applies key-rotation annotations/labels; applies global and device-set placement; applies same-node affinity; enables HostIPC for cryptsetup/udev synchronization; and removes duplicate env vars.

`makeKeyRotationCronJob()` wraps the pod template in a `batch.CronJob` with `ForbidConcurrent`, default `@weekly` schedule, and OSD resources. `reconcileKeyRotationCronJob()` deletes all key-rotation CronJobs when disabled. When enabled, it lists PVC-backed OSD Deployments, extracts OSD info and PVC name, rebuilds OSD props from device sets, skips unencrypted OSDs, creates a CronJob, sets the OSD Deployment as owner, and create-or-updates it.

## Control Flow
The reconcile path is all-or-error: list failures, bad OSD info, missing PVC label, config generation failure, owner-reference failure, or create/update failure return errors. Unencrypted OSDs are skipped. Disabled reconciliation performs collection deletion by app label and ignores not found.

## State and Persistence
Persistent state is Kubernetes CronJobs owned by OSD Deployments. Pod template labels, annotations, volumes, affinity, and schedule encode rotation behavior. The job uses mounted host data and block devices; secrets are accessed through KMS env/config integration, not by this file directly.

## Dependencies and Integration Points
The file depends on env helpers, KMS helpers, Kubernetes batch/core APIs, Rook placement/annotation/label APIs, Multus helpers, Deployment-derived OSD info from `osd.go`, PVC labels from `labels.go`, and encryption path helpers from neighboring OSD code.

## Risks and Edge Cases
Same-node placement is critical; incorrect labels or affinity can schedule rotation away from the device. The host path is built from `DataDirHostPath`, namespace, PVC name, and OSD ID, so layout changes affect rotation. Only PVC-backed encrypted OSDs are reconciled. Deleting all CronJobs when disabled uses an app label, so label drift can leave orphaned jobs.

## Test Signals
`key_rotation_test.go` covers name formatting and placement mutation. Full container, pod template, KMS, owner reference, and reconcile behavior are not deeply unit-tested in the listed files.
