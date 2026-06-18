# sources/control-plane/external-snapshotter/cmd/snapshot-controller/main.go

## Purpose
Main entrypoint for the cluster-level snapshot controller that reconciles VolumeSnapshot, VolumeSnapshotContent, and optionally group snapshot APIs.

Source size: 383 lines, 14849 bytes.

## Important APIs, Types, and Functions
- Go package `main`.
- Types/interfaces: `promklog`.
- Functions/methods: `ensureCustomResourceDefinitionsExist`, `main`, `buildConfig`, `Println`.
- Key imports: `context`, `flag`, `fmt`, `math`, `net`, `net/http`, `os`, `os/signal`, `strings`, `sync`, `time`, `k8s.io/client-go/informers/core/v1`, ...

## Control Flow
- Parses kubeconfig, logging, feature gates, worker counts, retry, leader election, metrics, distributed snapshotting, and volume-mode conversion flags.
- Builds clients and informer factories, optionally includes node informers, registers metrics and snapshot types, and constructs the common snapshot controller.
- Waits for required CRDs to exist with exponential backoff before running.
- Runs controller workers either under leader election or directly, starts informers/metrics HTTP server, and handles shutdown signals.

## State and Persistence
- Uses informer caches, workqueues, metrics, leader-election leases, and Kubernetes API writes to reconcile snapshot object status and bindings.
- The API server stores CRDs and snapshot objects; this process stores only transient cache/queue state.
- Distributed snapshotting adds node informer state for node-local volume handling.

## Dependencies and Integration Points
- Kubernetes client-go, generated snapshot client/informers, common-controller package, csi-lib-utils leader election, external-snapshotter metrics/features.

## Risks and Edge Cases
- Startup fails if CRDs are absent beyond `retry-crd-interval-max`.
- RBAC must allow list/watch/update on all snapshot and related core resources.
- Preventing volume-mode conversion is security-sensitive and should stay enabled unless deliberately changed.

## Test Signals
- CRD presence check is deterministic but needs API-server integration for full coverage.
- Controller behavior is tested in package-level controller tests outside this file.
