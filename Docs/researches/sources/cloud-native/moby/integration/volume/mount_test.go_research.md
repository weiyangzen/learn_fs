# sources/cloud-native/moby/integration/volume/mount_test.go

## Purpose
Exercises volume and image mount subpath behavior, including safe path validation, symlink escape prevention, file mounts, copy-up behavior, image mount removal semantics, multiple image mounts, and daemon restart persistence for image subpaths.

## Important APIs, Types, And Functions
- `TestRunMountVolumeSubdir` creates a populated test volume and table-tests valid/invalid `mount.VolumeOptions.Subpath` cases.
- `TestRunMountImage` builds a test image and table-tests `mount.ImageOptions.Subpath`, image removal while mounted, and force removal plus restart.
- `setupTestVolume` creates files, directories, and symlinks inside a named volume.
- `setupTestImage` builds a scratch image with files and symlinks using `fakecontext`.
- `TestRunMountImageMultipleTimes` mounts `hello-world:frozen` at two destinations in one container.
- `TestRunMountImageSubpathDaemonRestart` restarts a snapshotter daemon and verifies an image subpath mount survives.

## Control Flow
Tests build or create backing data, create containers with `HostConfig.Mounts`, branch on expected create/start errors, start containers, collect output, inspect exit code and mounts, and perform cleanup. Image removal cases inspect image IDs and restart containers. The daemon-restart test starts a separate daemon, runs a long-lived container with restart policy, restarts the daemon, inspects mounts/running state, and execs into the container.

## State And Persistence
State includes named volumes with filesystem content, built images, image mount references, container mount metadata, image deletion state, and daemon restart persistence. Symlinks inside volumes/images are used to test safe-path traversal.

## Dependencies And Integration Points
Depends on API versions 1.45 for volume subpaths and 1.48 for image mounts, `safepath` error types, container helpers, fake build contexts, daemon helpers, snapshotter mode for restart test, and frozen images.

## Risks And Edge Cases
Several cases skip Windows because file bind/image mounts or copy behavior differ. Safe-path tests are sensitive to symlink and path-cleaning behavior. The daemon-restart image-subpath test skips rootless and non-snapshotter modes due to known issue coverage.

## Test Signals
Passing signals include expected stdout from mounted subpaths/files, expected create/start errors for path escape or missing paths, image-in-use errors without force, successful restart after force image removal, two inspectable image mounts, and image subpath availability after daemon restart.
