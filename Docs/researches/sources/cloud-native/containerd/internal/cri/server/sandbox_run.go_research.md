# sources/cloud-native/containerd/internal/cri/server/sandbox_run.go

## Purpose

This file implements CRI `RunPodSandbox`, including ID/name reservation, lease creation, sandbox metadata persistence, network namespace and CNI setup, sandbox controller creation/start, NRI notification, store insertion, events, and helper conversion functions.

## Important APIs, Types, and Functions

`RunPodSandbox` is the main CRI entrypoint. Helpers include `ensurePauseImageExists`, `getNetworkPlugin`, `setupPodNetwork`, `cniNamespaceOpts`, `toCNILabels`, `toCNIBandWidth`, `toCNIPortMappings`, `toCNIDNS`, `selectPodIPs`, `ipString`, and `logDebugCNIResult`.

## Control Flow

The run path generates an ID, reserves the sandbox name, creates a lease, resolves runtime/sandboxer, stores metadata extension, creates and configures a network namespace when not host networking, runs CNI setup, creates the sandbox through the sandbox service, ensures the pause image unless disabled, starts the sandbox, stores returned labels/spec, runs NRI, marks ready, inserts into the store, sends created/started events, starts an exit monitor, and rolls back on errors.

## State and Persistence Behavior

It creates leases, sandbox-store records, netns mounts, CNI allocations, controller resources, in-memory sandbox store entries, labels/spec, process labels, and event records. Defers clean up name reservations, leases, metadata, CNI, netns, and started sandboxes on failure.

## Dependencies and Integration Points

It integrates with CRI config, sandbox service/controllers, containerd leases and sandbox store, CNI, NRI, tracing, metrics, image service, and CRI events.

## Risks and Test Signals

Risks include complex rollback ordering, user namespace netns setup, CNI partial failures, and pause image policy. Tests cover CNI conversion, IP selection, and disable-pause-image-pull config; integration tests cover the full path.
