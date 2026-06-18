# sources/cloud-native/moby/daemon/create_windows.go

## Purpose
Provides Windows-specific container create behavior. It applies the daemon default isolation mode when the caller left isolation unset and creates image-declared volumes without Unix-style rootfs content population.

## Important APIs, Types, And Functions
- `createContainerOSSpecificSettings` fills `HostConfig.Isolation` from `daemon.defaultIsolation`.
- `createContainerVolumesOS` parses raw volume specs with the Windows-aware volume parser, skips already-mounted destinations, creates volumes, and records mount points.

## Control Flow
During create, the OS settings hook normalizes default isolation. Volume setup iterates image `Config.Volumes`, parses each destination, skips `--volumes-from`/existing mounts, creates a volume in the configured driver, and adds it to `ctr.MountPoints`. The commented section explains that copying pre-existing container filesystem content into Windows volumes is intentionally deferred because path-following and HCS behavior do not support that flow.

## State And Persistence
Mutates host config isolation and container mount metadata, and creates persistent volume service records/backing storage. Unlike Unix, it does not mount the rootfs or copy initial data from image paths into volumes.

## Dependencies And Integration Points
Depends on `volume/mounts` parsing, volume service creation, daemon default isolation from `daemon_windows.go`, and the generic create pipeline in `create.go`.

## Risks And Edge Cases
Windows containers built with files under a Dockerfile `VOLUME` destination may not get those contents copied to the volume, and HCS may later reject mapped directories with contents. Incorrect default isolation would affect whether later mount/cleanup paths run on the host or inside a utility VM.

## Test Signals
Signals are mostly Windows integration tests for create/start with process and Hyper-V isolation and image-declared volumes; direct unit tests are absent in this file.
