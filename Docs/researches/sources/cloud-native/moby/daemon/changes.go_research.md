# sources/cloud-native/moby/daemon/changes.go

## Purpose
Implements the daemon API for returning filesystem changes for a container.

## Important APIs, Types, And Functions
Defines `(*Daemon) ContainerChanges(ctx, name) ([]archive.Change, error)`.

## Control Flow
The method records start time, resolves the container, rejects running containers on Windows, delegates diff computation to `daemon.imageService.Changes`, records the `changes` metric, and returns the change list.

## State And Persistence
No direct persistence. It reads container/image layer state through `imageService` and updates metrics.

## Dependencies And Integration Points
Integrates daemon container lookup, image service diffing, platform flag `isWindows`, archive change types, and container action metrics.

## Risks And Test Signals
Windows running-container rejection is a platform-specific behavior. Errors from container lookup or image diff pass through. Tests are outside this subset; expected signals are API diff responses and metric updates.
