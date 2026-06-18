# sources/cloud-native/moby/daemon/volumes.go

## Purpose
Core daemon logic for translating a container's persisted and requested volume, bind, tmpfs, image, cluster, and named-pipe mounts into `container.MountPoints`.

## Important APIs and Types
Defines `mountSort`, `sortMounts`, `(*Daemon).registerMountPoints`, `(*Daemon).lazyInitializeVolume`, `(*Daemon).VolumesService`, `volumeMounter`, and `volumeWrapper`. `volumeWrapper` adapts `api/types/volume.Volume` plus `service.VolumesService` methods to the daemon volume interface used by mountpoints.

## Control Flow, State, and Persistence
`registerMountPoints` copies existing mountpoints, overlays `VolumesFrom`, legacy `HostConfig.Binds`, then structured `HostConfig.Mounts`. Duplicate destinations release prior volume references. Volume mounts call the volume service with container references, bind mounts may be marked skip-create, and image mounts resolve an image, create a hashed RW layer, mount it read-only, and store layer metadata on the mountpoint. On error, newly referenced volumes are released. Finally it locks the container only to swap `ctr.MountPoints` and release replaced backward-compatible volumes.

## Dependencies, Integration Points, Risks, and Test Signals
Integrates with `volume/service`, mount parsers, image/layer services, `errdefs`, and platform-specific `validateBindDaemonRoot`/`setBindModeIfNull`. Risks include leaked volume refs on partial failure, destination shadowing, daemon-root bind propagation, image-layer cleanup, and duplicate bind/tmpfs targets. Tests in this group and integration mount tests validate parser behavior, mount creation, volume deletion semantics, and platform propagation.
