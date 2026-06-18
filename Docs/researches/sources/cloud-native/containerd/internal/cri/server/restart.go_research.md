# sources/cloud-native/containerd/internal/cri/server/restart.go

## Purpose

This file reconstructs CRI service state after containerd/CRI plugin restart, loading sandboxes, containers, images, IO, name indexes, exit monitors, and orphaned directories.

## Important APIs, Types, and Functions

`recover` loads old pause-container sandboxes, new sandbox-store records, running wait monitors, containers, and images. `loadContainer` reconstructs container metadata, status, IO, task state, and wait channels. `podSandboxRecover` is the controller recovery interface. `getNetNS`, `cleanupOrphanedIDDirs`, and `createContainerIO` support recovery.

## Control Flow

Recovery lists sandbox containers, delegates each to the podsandbox controller, then reconciles sandbox-store records not already loaded. It starts wait monitors for ready sandboxes, loads containers in parallel, validates task/checkpoint consistency, checks images, and removes orphaned root/state directories. Per-container loads are capped by a ten-second timeout.

## State and Persistence Behavior

It repopulates in-memory sandbox/container stores and name indexes from containerd metadata and status checkpoints. It may delete created/stopped tasks, update unknown container status, attach IO, and remove orphaned directories.

## Dependencies and Integration Points

It integrates with containerd container APIs, sandbox service, podsandbox recovery, CRI store/checkpoint types, image service, netns, typeurl metadata, errgroup concurrency, and filesystem cleanup.

## Risks and Test Signals

Risks include stale checkpoints, races with task deletion, leaked shims, missing metadata extensions, and accidental cleanup of directories for externally modified containers. Recovery tests and restart integration tests are essential.
