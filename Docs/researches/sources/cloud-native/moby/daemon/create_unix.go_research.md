# sources/cloud-native/moby/daemon/create_unix.go

## Purpose
Provides Unix-specific container create behavior: default masked/readonly Linux paths, initial container mount, working-directory setup, anonymous volume creation, SELinux relabeling, and image-to-volume data population.

## Important APIs, Types, And Functions
- `createContainerOSSpecificSettings` applies default Linux masked and readonly paths for non-privileged containers.
- `createContainerVolumesOS` mounts the container rootfs, creates missing anonymous volumes from image `Config.Volumes`, rejects volume-over-file cases, relabels volume paths, and delegates population.
- `populateVolumes` and `populateVolume` copy initial directory contents from the container image into volume mounts that request copy data.

## Control Flow
The create hook sets OCI default masked/readonly paths only when the host config did not already set them and the container is not privileged. Volume setup mounts the container, defers unmount, creates the working directory with daemon identity mapping, iterates declared image volumes, skips destinations already covered by `--volumes-from`, validates the destination path, creates a daemon volume, relabels it, records the mount point, then copies image contents into eligible named/anonymous volumes.

## State And Persistence
This file mutates `ctr.HostConfig`, `ctr.MountPoints`, the container working directory, volume service metadata, volume backing directories, SELinux labels, and volume contents. Population temporarily sets up and later cleans up each volume mount.

## Dependencies And Integration Points
Uses OCI default spec data, daemon `Mount`/`Unmount`, `container.GetResourcePath`, `volumes.Create`, `volumeopts.WithCreateReference`, SELinux `label.Relabel`, id-mapped mount setup, and `CopyImagePathContent`.

## Risks And Edge Cases
Volume setup depends on a successful temporary rootfs mount. Existing files at image volume destinations are rejected because a directory volume cannot be mounted over a file. Copying ignores missing mount sources but surfaces other mount setup errors. Deferred cleanup uses a context that ignores cancellation to avoid leaking mounted volumes.

## Test Signals
Coverage is mainly integration-level: container create with image-declared volumes, copy-data behavior, SELinux relabeling, working-directory creation, and cleanup after create failures.
