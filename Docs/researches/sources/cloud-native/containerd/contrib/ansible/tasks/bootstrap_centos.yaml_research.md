<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/tasks/bootstrap_centos.yaml -->
# sources/cloud-native/containerd/contrib/ansible/tasks/bootstrap_centos.yaml

## Purpose
CentOS bootstrap package installation for CRI/containerd test hosts.

## Important APIs, Types, And Functions
Ansible package task list.

## Control Flow
Installs required packages via yum/dnf.

## State And Persistence
Mutates system package set.

## Dependencies And Integration Points
CentOS package manager and repositories.

## Risks And Test Signals
Package names/repos can drift. Manual provisioning coverage. Source size reviewed: 12 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/tasks/bootstrap_centos.yaml -->
