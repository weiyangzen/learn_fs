# sources/control-plane/mayastor/terraform/mod/k8s/master.sh

Purpose: bootstraps the Kubernetes control-plane node for Terraform-provisioned test clusters.

Important APIs/types/functions: runs `kubeadm init --config /tmp/kubeadm_config.yaml` with swap/CPU/system verification preflight ignores, installs kubeconfig into `$HOME/.kube/config`, waits for localhost port 6443 with `nc`, and applies kube-router daemonset from GitHub.

Control flow: `set -ex` aborts on failures; after kubeadm init it loops until API server is reachable, then installs networking.

State/persistence: creates Kubernetes control-plane state, user kubeconfig, and cluster network daemonset.

Dependencies/integration: depends on `repo.sh` package setup, rendered kubeadm config, network access to GitHub, kubeadm/kubectl/nc.

Risks: applying a remote master-branch kube-router manifest is not pinned and can drift. Ignores significant preflight errors.

Test signals: local `kubectl` should work and kube-router pods should be created.
