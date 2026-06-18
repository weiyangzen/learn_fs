# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvs/service.go

## Purpose
This file defines PV dashboard DTOs, the `PVService` interface, and the factory for cached vs uncached implementations.

## Important APIs, Types, And Functions
It defines `ListPVPodResult`, `PVService`, and `NewPVService`.

## Control Flow
`NewPVService` creates a base `pvService`; when manager mode is enabled, it wraps it in `CachePVService` with a time-ordered PV index.

## State And Persistence
Factory state is either a plain client service or an indexed cached service. No Kubernetes resources are mutated.

## Dependencies And Integration Points
It is used by `API.NewAPI`, `pv.go`, `pod.go`, and `batch.go`. It depends on corev1 PV types, Gin, controller-runtime client, and dashboard index utilities.

## Risks
The result type includes both `Total` and Kubernetes `Continue`, but cached and uncached modes populate different fields. Consumers should treat these as mode-dependent.

## Test Signals
No tests are present. Factory and JSON result behavior are low-cost test targets.
