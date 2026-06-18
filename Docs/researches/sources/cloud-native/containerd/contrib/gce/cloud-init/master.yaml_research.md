<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/gce/cloud-init/master.yaml -->
# sources/cloud-native/containerd/contrib/gce/cloud-init/master.yaml

## Purpose
GCE cloud-init config for bootstrapping a Kubernetes/containerd master node.

## Important APIs, Types, And Functions
Cloud-init users, write_files for systemd units/config scripts, and runcmd startup commands.

## Control Flow
Creates service units for containerd installation/runtime/target and Kubernetes master installation, downloads metadata-provided configure scripts, enables targets, and runs bootstrapping commands.

## State And Persistence
Writes systemd units, users, scripts, services, and starts installation on a VM.

## Dependencies And Integration Points
GCE metadata server, systemd, curl, Kubernetes/containerd install artifacts.

## Risks And Test Signals
Metadata script URLs and legacy Kubernetes assumptions can drift; running it mutates a VM heavily. Validation is cloud-init boot success. Source size reviewed: 200 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/gce/cloud-init/master.yaml -->
