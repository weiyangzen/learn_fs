# sources/cloud-native/moby/daemon/mounts.go

## Purpose
This file prepares persisted mount-point state before container use and releases/removes volume and image mounts during cleanup.

## Important APIs, Types, And Functions
`Daemon.prepareMountPoints` lazy-initializes volumes, restores image mount layers, and live-restores volumes for running containers. `Daemon.removeMountPoints` releases volume references, removes anonymous volumes when requested, unmounts image layers, and releases image layers.

## Control Flow
Preparation iterates all mount points, initializes each volume, restores missing image layers from `imageService.GetLayerByID`, skips non-volume mount points, and calls `LiveRestore` for volumes on already-running containers. Removal iterates mount points, releases volume refs, optionally removes anonymous volumes while ignoring in-use errors, then unmounts and releases image layers or records a missing-layer error.

## State, Persistence, And Dependencies
The code mutates mount point runtime references (`Layer`, live-restored volume state) and affects volume/image-layer reference counts through volume service and image service. Errors are aggregated as strings and returned as one formatted error.

## Integration Points
This file connects container restore/removal paths with daemon volume service, image service, mount API types, and live-restore behavior.

## Risks And Edge Cases
Named volumes are never removed even when `rm` is true. Anonymous volume removal ignores in-use errors to avoid noisy failure when shared with other containers. Missing image layer references become cleanup errors. Live restore only runs for containers whose state says running.

## Test Signals
No direct tests in this item. Indirect coverage comes from container restore/removal and volume/image mount integration tests.
