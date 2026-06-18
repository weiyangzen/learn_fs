# sources/control-plane/juicefs-csi-driver/pkg/dashboard/api.go

## Purpose
This file defines the dashboard API object, wires Kubernetes clients and service implementations, and registers all REST and websocket routes.

## Important APIs, Types, And Functions
`API` stores namespace, manager mode, cached/controller clients, a typed `k8sclient`, REST config, and service interfaces for pods, PVs, PVCs, secrets, jobs, and events. `NewAPI` constructs services, `Handle` registers routes, and `getVersion` returns driver version data.

## Control Flow
`NewAPI` creates a `k8sclient` from the REST config and chooses cached or uncached services based on `enableManager`. `Handle` attaches top-level list/config/version routes, scoped pod/PV/PVC/storageclass groups with middleware, batch upgrade routes, cache-group routes, and websocket endpoints for logs, exec, debug, warmup, stats, smooth upgrade, and access logs.

## State And Persistence
The `API` object holds process-local service references and client handles. It does not persist data directly; handlers persist through Kubernetes resources such as ConfigMaps, Jobs, node labels, Secrets, and Pods.

## Dependencies And Integration Points
It integrates Gin routing, controller-runtime clients, Kubernetes REST config, driver versioning, and the dashboard service packages. Route groups are the central integration surface for `pod.go`, `pv.go`, `cm.go`, `batch.go`, and `cache_group.go`.

## Risks
`NewAPI` returns nil if client construction fails, so callers must check before routing. The route surface exposes powerful pod exec and cluster mutation endpoints; deployment authentication/authorization must be enforced outside these handlers. Cached mode changes pagination semantics from continue tokens to current/page-size pages.

## Test Signals
No route registration tests are in this subset. Useful tests would assert route presence, nil-client behavior, and cached/uncached service selection.
