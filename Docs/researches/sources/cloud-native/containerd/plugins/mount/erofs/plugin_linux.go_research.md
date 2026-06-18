# sources/cloud-native/containerd/plugins/mount/erofs/plugin_linux.go

## Purpose
Registers a Linux EROFS mount handler supporting raw file-backed mounts, loop-device fallback, multi-device options, fsmount fallback, and optional dm-verity device setup/cleanup.

## Important APIs, Types, And Functions
`erofsMountHandler` implements `mount.Handler`. `Mount` handles EROFS mount activation. `setupDmVerityDevice`, `waitForDevice`, `doMount`, and `Unmount` manage dm-verity and mount syscalls. `Config` is empty plugin config.

## Control Flow
Mount rejects non-EROFS types, parses `X-containerd.dmverity=`, reads metadata and opens/reuses a dm-verity device when present, filters internal options, creates the mount point, tries file-backed fsmount unless loop fallback is forced, on `ENOTBLK` sets up loop devices for source and `device=` options, mounts, and returns `ActiveMount`. Unmount looks up the source, unmounts, and closes matching `/dev/mapper/containerd-erofs-*` devices.

## State And Persistence
Mount state is kernel state plus loop/dm-verity devices. It creates mount-point directories and may create device-mapper devices. `forceloop` is process-global after raw file mount fails.

## Dependencies And Integration Points
Uses core mount APIs, `internal/dmverity`, `internal/fsmount`, Unix errors, plugin registry, and EROFS differ sidecar metadata.

## Risks
Device-mapper cleanup is best-effort and tied to source naming. `forceloop` globally changes future behavior. Loop device setup for `device=` options must match multi-device EROFS images. Mount requires Linux kernel support and privileges.

## Test Signals
`plugin_linux_test.go` covers fsmount loop-device mounting and fsmount behavior with long option lists under privileged Linux environments.
