<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/vars/vars.yaml -->
# sources/cloud-native/containerd/contrib/ansible/vars/vars.yaml

## Purpose
Shared Ansible variables for containerd release and CNI directories.

## Important APIs, Types, And Functions
Defines `containerd_release_version`, `cni_bin_dir`, and `cni_conf_dir`.

## Control Flow
Consumed by playbook/task includes during provisioning.

## State And Persistence
No execution; controls remote filesystem paths and download version.

## Dependencies And Integration Points
Ansible variable resolution.

## Risks And Test Signals
Pinned version `1.5.5` may be stale for modern containerd tests. Source size reviewed: 4 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/vars/vars.yaml -->
