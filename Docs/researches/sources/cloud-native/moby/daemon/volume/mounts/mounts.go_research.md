# sources/cloud-native/moby/daemon/volume/mounts/mounts.go

## Purpose
Defines the persistent `MountPoint` model and runtime setup/cleanup behavior connecting container mount declarations to volume, bind, image, and layer resources.

## Important APIs, Types, And Functions
`RWLayer` abstracts writable layer mount/unmount. `MountPoint` stores persisted mount metadata plus runtime fields (`Volume`, `active`, `safePaths`, `Layer`). Methods include `Cleanup`, `Setup`, `LiveRestore`, and `Path`.

## Control Flow
`Setup` returns source directly when mountpoint creation is skipped. For volumes it generates/reuses an ID, calls `Volume.Mount`, optionally wraps `VolumeOptions.Subpath` with `safepath.Join`, increments `active`, and returns a cleanup callback for the safe path. For image mounts with subpaths it uses `safepath.Join` over the image source. For bind mounts it optionally runs `checkFun`, then best-effort creates missing host directories with remapped root ownership. A deferred relabel block evaluates symlinks and applies SELinux labels when requested, cleaning up on relabel errors. `Cleanup` closes any valid safe paths, calls `Volume.Unmount`, decrements active count, and clears ID at zero. `LiveRestore` calls optional `volume.LiveRestorer` and increments active.

## State And Persistence
`MountPoint` is embedded in container state and persisted, but `Volume`, `safePaths`, and `Layer` are runtime-only. Setup mutates mount IDs, active counters, and may create host bind directories or temporary safe mounts.

## Dependencies And Integration Points
Integrates parsers, volume drivers, safepath, idtools, user chown helpers, SELinux labeling, string IDs, and container layer code.

## Risks
Mount/unmount reference counting and safe path cleanup are security-sensitive. Subpath handling must avoid TOCTOU and use-after-close. Bind auto-creation can create directories where files were intended. Relabel failure handling must clean up temporary resources correctly.

## Test Signals
Parser and safepath tests cover inputs feeding `Setup`; direct setup behavior is primarily covered by higher-level daemon/container integration tests outside this subset.
