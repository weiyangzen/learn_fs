# sources/cloud-native/moby/daemon/volumes_unix.go

## Purpose
Unix, non-Windows mount setup for starting containers.

## Important APIs and Types
Defines `(*Daemon).setupMounts` and Unix `setBindModeIfNull`.

## Control Flow, State, and Persistence
`setupMounts` collects tmpfs destinations, skips mountpoints covered by tmpfs, lazily restores volume handles, rejects daemon-host socket mounts during shutdown, and calls each mountpoint's `Setup` with mount label and remapped root identity. Cleanup callbacks are accumulated and released only on success. Non-network mounts are converted to `container.Mount` entries with bind recursion/read-only flags and volume mount events; network mounts are recorded on the container and appended after sorting. Network files under the daemon repository are chowned for user namespace remapping.

## Dependencies, Integration Points, Risks, and Test Signals
Depends on `cleanups.Composite`, id mapping, `volumemounts.MountPoint.Setup`, container network mount detection, and daemon volume events. Risks include cleanup leaks, incorrect read-only recursive option combinations, userns ownership failures, and ordering that could shadow nested mounts. Integration mount tests and daemon start tests exercise this path indirectly. `setBindModeIfNull` defaults local named volumes to SELinux shared label `z`.
