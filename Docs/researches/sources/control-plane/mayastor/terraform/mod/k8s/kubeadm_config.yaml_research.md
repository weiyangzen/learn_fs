# sources/control-plane/mayastor/terraform/mod/k8s/kubeadm_config.yaml

Purpose: templated kubeadm configuration for creating a Kubernetes cluster.

Important APIs/types/functions: `InitConfiguration` sets bootstrap token, API advertise address `${master_ip}`, and bind port 6443. `ClusterConfiguration` sets API timeout, cert SAN `${cert_sans}`, cluster name `gilanetes`, and pod subnet `${pod_cidr}`. `KubeletConfiguration` sets systemd cgroup driver and `failSwapOn: false`.

Control flow: consumed by `kubeadm init --config`.

State/persistence: creates cluster certificates/config and kubelet config on the master.

Dependencies/integration: rendered by Terraform and used by `master.sh`; token must match node join script.

Risks: kubeadm API version `v1beta2` may be unsupported by newer Kubernetes. `certSANs` as a single templated scalar must render valid YAML.

Test signals: `kubeadm init` should complete and nodes should join with the same token and pod CIDR.
