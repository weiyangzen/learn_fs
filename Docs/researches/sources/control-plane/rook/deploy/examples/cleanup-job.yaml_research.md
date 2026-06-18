
# sources/control-plane/rook/deploy/examples/cleanup-job.yaml

Purpose: provides a manual per-node cleanup `Job` that runs Rook's `ceph clean host` logic when operator-managed cleanup did not run or a node needs explicit cleanup.

Important APIs/types/functions: Kubernetes `batch/v1` `Job`, service account `rook-ceph-default`, nodeSelector `kubernetes.io/hostname`, privileged root container `docker.io/rook/ceph:master`, args `["ceph", "clean", "host"]`, hostPath volumes for the Rook data directory, `/dev`, and `/run/udev`, and env vars sourced from `rook-ceph-mon` secret.

Control flow: the user replaces placeholders for job name, node hostname, and dataDirHostPath, then applies one job per node. The pod is pinned to that node, mounts host storage/devices, reads monitor secret and FSID, and sanitizes Rook/Ceph data according to env settings.

State and persistence: the Job persists execution history; the container mutates host disk and Rook data state destructively. Sanitization settings determine how much on-disk metadata is removed.

Dependencies/integration: depends on an existing cluster namespace, `rook-ceph-mon` secret keys `mon-secret` and `fsid`, matching `spec.dataDirHostPath`, udev/dev access, and privileged pod admission.

Risks: this is destructive and placeholder mistakes can clean the wrong node or path. The `master` image tag is moving. Privileged hostPath access is sensitive, and reclaim policies may leave PVs behind.

Test signals: dry-run render after replacing placeholders, verify node selection, inspect logs for FSID/path detection, and confirm target host data/device metadata is removed only on the intended node.
