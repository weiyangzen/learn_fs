<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/containerd.service -->
# sources/cloud-native/containerd/containerd.service

## Purpose
Systemd unit for running containerd as a Linux service.

## Important APIs, Types, And Functions
Defines Unit, Service, and Install sections with `ExecStart=/usr/local/bin/containerd`.

## Control Flow
Starts after network/local filesystems, delegates cgroups, adjusts OOM score and limits, preloads overlay module, and restarts according to systemd policy.

## State And Persistence
Systemd manages process lifecycle, logs, cgroups, and enabled target symlink state.

## Dependencies And Integration Points
systemd, modprobe overlay, `/usr/local/bin/containerd`.

## Risks And Test Signals
Hard-coded binary path must match installation; high resource limits and Delegate are required for containers. Tested by packaging/system integration. Source size reviewed: 41 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/containerd.service -->
