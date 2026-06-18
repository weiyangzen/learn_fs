# sources/control-plane/juicefs-csi-driver/pkg/dashboard/services/pods/service.go

## Purpose
This file defines dashboard pod DTOs, the `PodService` interface, and the factory that chooses cached or uncached implementations.

## Important APIs, Types, And Functions
It defines `PodExtra`, `ListAppPodResult`, `ListSysPodResult`, a service-local `PodDiff`, `PodService`, and `NewPodService`.

## Control Flow
`NewPodService` builds a base `podService`. In manager mode it returns `CachePodService` with indexes and CSI-node map. Outside manager mode it tries to list a CSI node pod immediately and stores the first pod spec in `config.CSIPod`, then returns the base service.

## State And Persistence
Factory-created state is client/config handles and, in cached mode, in-memory indexes. `config.CSIPod` is process-global state initialized from observed CSI node pods. No Kubernetes mutation occurs.

## Dependencies And Integration Points
The interface is consumed by dashboard handlers in `pod.go`, `pv.go`, `cm.go`, and `batch.go`. It depends on Kubernetes API types, Gin, REST config, dashboard utilities, and `k8sclient`.

## Risks
The interface has a parameter typo `ontainer` for `ExecPod`, harmless for compilation but confusing. Cached and uncached services differ in pagination and enrichment behavior. Initialization logs and falls back silently if no CSI node pod is available in uncached mode.

## Test Signals
No direct tests are present. Tests should verify factory selection and `config.CSIPod` initialization behavior.
