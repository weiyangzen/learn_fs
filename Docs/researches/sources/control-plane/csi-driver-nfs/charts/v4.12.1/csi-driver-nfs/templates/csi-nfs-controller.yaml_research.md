# sources/control-plane/csi-driver-nfs/charts/v4.12.1/csi-driver-nfs/templates/csi-nfs-controller.yaml

## Purpose
This Deployment template runs the NFS CSI controller for chart 4.12.1, including provisioner, resizer, optional snapshotter, liveness probe, and privileged NFS CSI server containers.

## APIs, Control Flow, and State
It renders an `apps/v1` Deployment with controller labels, replica count, strategy, host networking, controller service account, scheduling knobs, Linux selector, priority, seccomp, tolerations, and shared `/csi` socket `emptyDir`. The provisioner uses leader election, `--extra-create-metadata=true`, `HonorPVReclaimPolicy=true`, timeout and retry settings. The resizer uses leader election and disables handling volume-in-use errors. The optional snapshotter shares the CSI socket. The `nfs` container receives node identity, CSI endpoint, driver name, mount permissions, working mount dir, delete policy, and tar snapshot mode.

## Dependencies and Integration Points
The 4.12.1 template is identical to 4.12.0; version behavior changes come from `values.yaml` image tags. It depends on RBAC, StorageClass configuration, kubelet pod hostPath, and snapshot CRDs when snapshots are enabled.

## Risks and Test Signals
Host network, privileged SYS_ADMIN, and bidirectional kubelet mounts expand the blast radius. Test with Helm lint/template, pod security admission policy, controller readiness, PVC provisioning, expansion, snapshot creation, and sidecar leader election.
