# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pvcs/service.go

## Purpose
This file defines PVC dashboard DTOs, the `PVCService` interface, and the cached/uncached factory.

## Important APIs, Types, And Functions
It defines `ListPVCResult`, `ListPVCWithPodResult`, `PVCWithPod`, `PVCBasicInfo`, `ListPVCBasicResult`, `PVCService`, and `NewPVCService`.

## Control Flow
`NewPVCService` creates a base `pvcService`; manager mode wraps it in `CachePVCService` with a time-ordered PVC index.

## State And Persistence
Only service object state is created. PVC data persists in Kubernetes and is not mutated by this file.

## Dependencies And Integration Points
It is consumed by PV/config/batch handlers and depends on Gin contexts, corev1 types, controller-runtime client, and dashboard index utilities.

## Risks
The interface hides cached/uncached differences in pagination and filtering. Some DTOs such as `ListPVCWithPodResult` are defined here but not used in the visible handlers, so schema drift is possible.

## Test Signals
No tests are present. Factory behavior and DTO JSON shape are straightforward candidates.
