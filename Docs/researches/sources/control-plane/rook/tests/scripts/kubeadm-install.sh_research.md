<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/kubeadm-install.sh -->
# sources/control-plane/rook/tests/scripts/kubeadm-install.sh

Purpose: host setup helper for installing a specified Kubernetes version via kubeadm packages on Debian/Ubuntu-like runners.

Important APIs and control flow: it defaults `KUBE_VERSION` to `v1.15.12`, converts it to Debian package suffix form, defines `wait_for_dpkg_unlock`, configures package repositories/keys, installs kubelet/kubeadm/kubectl, and marks packages held.

State, persistence, and integration: mutates apt sources, package state, and system Kubernetes binaries. Dependencies include apt, curl, root privileges, and package repository availability. Risks include old default Kubernetes version, package repository drift, and host-level side effects. Test signals are successful package install and later kubeadm cluster creation.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/kubeadm-install.sh -->
