<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/tasks/binaries.yaml -->
# sources/cloud-native/containerd/contrib/ansible/tasks/binaries.yaml

## Purpose
Ansible tasks for downloading containerd and preparing CNI directories.

## Important APIs, Types, And Functions
Tasks using `unarchive`/file modules and shared vars.

## Control Flow
Fetches the containerd release tarball into root, creates CNI binary and config directories.

## State And Persistence
Writes binaries/directories on remote hosts.

## Dependencies And Integration Points
Ansible modules, GitHub release URL, vars `containerd_release_version`, `cni_*_dir`.

## Risks And Test Signals
Network/version drift and root permissions. Tested by running playbook. Source size reviewed: 12 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/ansible/tasks/binaries.yaml -->
