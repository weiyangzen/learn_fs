<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/cri-containerd.yaml -->
# sources/cloud-native/containerd/contrib/ansible/cri-containerd.yaml

## Purpose
Top-level Ansible playbook for provisioning a host with containerd CRI and Kubernetes dependencies.

## Important APIs, Types, And Functions
Ansible play referencing vars and task files.

## Control Flow
Loads shared variables, runs bootstrap, binary install, and Kubernetes task includes according to target distribution.

## State And Persistence
Mutates remote hosts: packages, directories, binaries, repos, and services.

## Dependencies And Integration Points
Ansible, distro package managers, Kubernetes repositories, containerd release artifacts.

## Risks And Test Signals
Versions are pinned/old in vars; playbook is contrib and may drift from current install guidance. Validated by manual/provisioning runs. Source size reviewed: 66 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/cri-containerd.yaml -->
