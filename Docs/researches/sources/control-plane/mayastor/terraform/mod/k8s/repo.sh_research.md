# sources/control-plane/mayastor/terraform/mod/k8s/repo.sh

Purpose: installs Docker, containerd, kubelet, kubeadm, and kubectl prerequisites on Ubuntu nodes.

Important APIs/types/functions: adds Google Kubernetes and Docker apt keys/repos, installs packages, marks Kubernetes packages held, writes Docker daemon config with systemd cgroup driver and overlay2, loads overlay/br_netfilter modules, writes containerd default config, and adds a systemd override intended for containerd kill behavior.

Control flow: updates apt, installs dependencies, writes config files, restarts Docker and containerd, and applies sysctl.

State/persistence: mutates apt sources/keys, packages, Docker/containerd configs, systemd drop-ins, modules-load config, and sysctl state.

Dependencies/integration: run before `master.sh` or `node.sh` in Terraform provisioning.

Risks: uses deprecated `apt-key` and old Kubernetes xenial repo. The containerd override path appears to write under `/etc/sysctl.d/system/containerd.service.d/override.conf` instead of `/etc/systemd/system/...`, likely a bug.

Test signals: kubeadm/kubectl/docker/containerd should be installed and using systemd cgroups.
