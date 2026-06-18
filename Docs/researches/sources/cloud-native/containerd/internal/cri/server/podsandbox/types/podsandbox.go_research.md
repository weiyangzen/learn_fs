# sources/cloud-native/containerd/internal/cri/server/podsandbox/types/podsandbox.go

## Purpose

This file defines the live pod sandbox object used by the controller, including wait/exit synchronization and mutable status storage.

## Important APIs, Types, and Functions

`PodSandbox` carries ID, containerd container, metadata, runtime options, status storage, and a stop channel. `NewPodSandbox` initializes status and immediately stops the wait channel for not-ready sandboxes. `Exit` updates state to not-ready, records exit status/time, clears PID, and stops waiters. `Wait` blocks until context cancellation or exit.

## Control Flow

`Wait` selects on context or the stop channel. `Exit` performs an atomic status update before signaling waiters.

## State and Persistence Behavior

Status is in-memory through `sandboxstore.StatusStorage`. Exit state can be reconstructed on recovery, but the stop channel is process-local.

## Dependencies and Integration Points

It integrates with containerd exit status values, sandbox runtime options, CRI sandbox metadata, and the generic store stop channel.

## Risks and Test Signals

Risks include callers waiting forever if `Exit` is never called and loss of wait channel state across restart. The unit test validates status mutation, wait timeout, and exit wakeup.
