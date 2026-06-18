# Research: sources/cloud-native/containerd/cmd/containerd-stress/cri_worker.go

## Purpose
Implements the CRI-based worker used by `containerd-stress` to repeatedly create and remove pod sandboxes through the Kubernetes CRI API.

## Important APIs, Control Flow, And State
`criWorker` tracks worker ID, counts, failures, CRI runtime client, runtime handler, snapshotter, and commit label. `run` loops until the timeout context is done, creates a sandbox ID, times `runSandbox`, records metrics on success, and increments errors on non-deadline failures. `runSandbox` builds `PodSandboxConfig`, calls `RunPodSandbox`, defers stop/remove, and starts a ticker goroutine that polls sandbox status until timeout. `criCleanup` lists sandboxes with the stress namespace label and stops/removes them. State is remote CRI sandbox state plus local counters.

## Dependencies And Integration
Uses integration `remote.RuntimeService`, CRI runtime v1 API, internal CRI ID utility, logging, and shared metrics from `main.go`.

## Risks And Test Signals
Risks include the ticker status condition appearing inverted, leaked ticker goroutines, cleanup aborting on first failure, and unsynchronized counters if accessed concurrently. Tests should cover run loop cancellation, sandbox config fields/labels, cleanup filtering, error counting, and polling goroutine exit.
