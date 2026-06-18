# sources/cloud-native/containerd/internal/cri/server/container_image_mount_other.go

## Purpose
This non-Linux image-volume helper provides portable behavior for platforms without Linux overlay volatile mounts or snapshot idmap remapper labels.

## Important APIs, Types, and Functions
`addVolatileOptionOnImageVolumeMount` is a no-op. `ensureImageVolumeMounted` treats any existing target path as mounted. `getImageVolumeSnapshotOpts` returns nil.

## Control Flow, State, and Persistence
The file performs only an existence check and returns default options. It does not inspect mount tables or mutate snapshot labels.

## Dependencies and Integration Points
It depends on `os.Stat`, containerd mount/snapshot types, and CRI mounts. It integrates with `mutateImageMount` as the `!linux` implementation.

## Risks and Test Signals
Risk is weaker mounted-state detection on non-Linux platforms, because an existing directory is considered sufficient. There are no direct tests in this subset; platform-specific runtime integration would be needed to validate non-Linux image volumes.
