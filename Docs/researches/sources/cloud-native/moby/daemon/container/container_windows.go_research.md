<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/container_windows.go -->
# sources/cloud-native/moby/daemon/container/container_windows.go

## Purpose
Implements Windows-specific container mount and update behavior for secrets, configs, volumes, tmpfs no-op handling, hostname no-op, and mount point API mapping.

## Important APIs, Types, And Functions
Constants for Windows secret/config mount paths and default stop timeout; `CreateSecretSymlinks`, `SecretMounts`, `UnmountSecrets`, `CreateConfigSymlinks`, `ConfigMounts`, `DetachAndUnmount`, `TmpfsMounts`, `UpdateContainer`, `BuildHostnameFile`, `GetMountPoints`, `ConfigsDirPath`, `ConfigFilePath`.

## Control Flow
Secrets/configs are exposed through internal mounts and symlinks at requested targets. Resource updates reject nearly all resource fields as unsupported on Windows, but allow restart policy changes subject to AutoRemove conflict rules.

## State And Persistence Behavior
Creates directories and symlinks inside the container rootfs, removes secret mount directories, mutates restart policy, and reports configs under `<container root>/configs`.

## Dependencies And Integration Points
Uses Windows archive path resolution, errdefs invalid-parameter errors, swarm refs, and volume unmount cleanup.

## Risks And Test Signals
Risks include symlink creation on hosts without privilege/support, no resource-update support except restart policy, and Windows configs not using secure secret storage. Windows integration tests should cover secrets/configs and update API behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/container/container_windows.go -->
