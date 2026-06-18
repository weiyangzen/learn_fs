<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/create-dev-cluster.sh -->
# sources/control-plane/rook/tests/scripts/create-dev-cluster.sh

Purpose: local developer helper for creating a Rook Ceph cluster on minikube. It supports custom namespaces, cluster spec selection, optional Rook orchestrator enablement, and monitoring setup.

Important APIs and control flow: environment variables configure minikube profile, disk size, node count, extra disks, examples dir, and namespaces. Functions initialize command aliases, rewrite namespace markers in example manifests, choose minikube driver by OS/architecture, create the cluster with CRDs/common/operator/cluster/toolbox/dashboard manifests, wait for operator and Ceph health, optionally enable the Ceph rook orchestrator and monitoring, and print dashboard/prometheus access details. Command options are `-f`, `-r`, `-m`, and `-h`.

State, persistence, and integration: creates/deletes a minikube profile, mutates files in the examples directory with `.bak` backups, applies Kubernetes resources, and changes the user's shell guidance. Dependencies include minikube, kubectl, envsubst, sed, base64, and Rook deploy examples. Risks include in-place manifest mutation, assumptions about minikube drivers, unquoted extra args, and infinite waits if health never reaches `HEALTH_OK`. Test signals are rollout status, cluster health, optional module status, and printed endpoints.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/create-dev-cluster.sh -->
