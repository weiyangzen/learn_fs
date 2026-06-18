# Research: sources/cloud-native/containerd/cmd/containerd-stress/worker.go

## Purpose
Implements the base non-CRI stress worker that repeatedly creates, starts, waits for, and deletes containers.

## Important APIs, Control Flow, And State
`ctrWorker` stores worker identity, counts, failures, client, image, commit, and snapshotter. `run` loops until timeout, calls `runContainer`, records metrics on success, and logs/counts non-deadline failures. `runContainer` creates a container with image spec and snapshot, creates a task with null IO, starts it, waits for exit, and deletes task/container with snapshot cleanup in defers. `getID` produces deterministic IDs from worker and count. State is remote container/task/snapshot lifecycle plus local counters.

## Dependencies And Integration
Uses containerd client APIs, `cio`, OCI spec helpers, logging, and metrics from `main.go`. It is the primary worker for normal stress runs and a base for exec workers.

## Risks And Test Signals
Risks include cleanup failures after partial creation, snapshot accumulation, blocking waits, and unsynchronized counter reads. Tests should cover successful lifecycle, create/task/start failures, deadline handling, cleanup defers, and ID generation.
