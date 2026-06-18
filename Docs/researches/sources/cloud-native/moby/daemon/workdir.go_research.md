# sources/cloud-native/moby/daemon/workdir.go

## Purpose
Backend helper for creating a container working directory on demand, mainly for builder flows.

## Important APIs and Types
Defines `(*Daemon).ContainerCreateWorkdir(cID string) error`.

## Control Flow, State, and Persistence
The method resolves a container, mounts its root filesystem, defers unmount, then calls `container.SetupWorkingDirectory` with the daemon's remapped root identity. It mutates container filesystem state by creating the configured workdir if needed.

## Dependencies, Integration Points, Risks, and Test Signals
Integrates with builder code that wants the daemon to handle workdir creation instead of paying the cost during general container setup. It depends on daemon mount/unmount paths and id mapping. Risks include leaving the rootfs mounted on error if defers do not run, userns ownership errors, and Windows performance regressions that motivated the helper. Build and container create integration tests are indirect signals.
