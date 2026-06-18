<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/container_unix.go -->
# sources/cloud-native/moby/daemon/container/container_unix.go

## Purpose
Implements Unix-specific container mounts, secret/config mount handling, resource updates, lazy unmounts, tmpfs conversion, hostname file creation, and mount point API mapping.

## Important APIs, Types, And Functions
Constants for default stop timeout and secret/config mount paths; `TrySetNetworkMount`, `BuildHostnameFile`, `NetworkMounts`, `CopyImagePathContent`, `ShmResourcePath`, `HasMountFor`, `UnmountIpcMount`, `IpcMounts`, `SecretMounts`, `UnmountSecrets`, `UpdateContainer`, `DetachAndUnmount`, `copyExistingContents`, `TmpfsMounts`, `GetMountPoints`, `ConfigFilePath`.

## Control Flow
Network mounts validate backing files, choose writability from rootfs or bind mount overrides, relabel when needed, and emit mount descriptors. Resource updates reject NanoCPU/CPUPeriod/CPUQuota conflicts, then selectively copy non-zero/non-nil resource fields and restart policy. Detach/unmount resolves mount destinations and unmounts them before volume cleanup.

## State And Persistence Behavior
Writes hostname files, relabels files, copies image contents into volumes, unmounts shm/secrets/volumes, and mutates `HostConfig.Resources` plus restart policy.

## Dependencies And Integration Points
Integrates Linux mount helpers, SELinux labels, containerd continuity copy, volume mount parser, swarm refs, and event logging for volumes.

## Risks And Test Signals
Risks include mount path resolution races, relabel failures except unsupported xattrs, resource zero-values meaning "no update", and memory/memoryswap conflict logic. Container update, mount, and swarm secret/config tests are downstream signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/container_unix.go -->
