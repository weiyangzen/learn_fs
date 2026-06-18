# sources/cloud-native/moby/daemon/volumes_windows.go

## Purpose
Windows implementation of mount setup and no-op platform hooks for bind mode and daemon-root propagation.

## Important APIs and Types
Defines Windows `(*Daemon).setupMounts`, `setBindModeIfNull`, and `validateBindDaemonRoot`.

## Control Flow, State, and Persistence
`setupMounts` walks container mountpoints, lazily initializes volume handles, calls `MountPoint.Setup` with empty identity and no validation callback, records temporary cleanups, and returns sorted `container.Mount` entries. Cleanup callbacks are invoked on setup failure and released on success. Unlike Unix, there is no network mount special handling, no SELinux mode default, and daemon-root bind propagation is always not needed.

## Dependencies, Integration Points, Risks, and Test Signals
Integrates with Windows runtime spec generation through daemon start. The file relies on `volumemounts` to implement Windows-specific validation and path handling. Risks include missing cleanup after setup errors, named-pipe or volume path normalization, and unsupported mount options. Windows integration tests in this group cover named-pipe bind validation and Windows-specific build/container behavior.
