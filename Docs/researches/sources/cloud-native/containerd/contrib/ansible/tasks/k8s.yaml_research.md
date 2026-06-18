<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/tasks/k8s.yaml -->
# sources/cloud-native/containerd/contrib/ansible/tasks/k8s.yaml

## Purpose
Ansible tasks for configuring Kubernetes repositories and installing kubelet/kubeadm/kubectl.

## Important APIs, Types, And Functions
Tasks for apt/yum repo keys, SELinux handling, and Kubernetes package installation.

## Control Flow
Branches on distro family: Ubuntu adds gpg key/source and apt update; CentOS adds yum repo, disables SELinux, and installs Kubernetes packages.

## State And Persistence
Writes repo files/keys, changes SELinux config, installs packages.

## Dependencies And Integration Points
Kubernetes package repos, distro package managers, Ansible facts.

## Risks And Test Signals
Repository key URLs and package names are time-sensitive; disabling SELinux is broad. Manual/provisioning test signal. Source size reviewed: 52 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/tasks/k8s.yaml -->
