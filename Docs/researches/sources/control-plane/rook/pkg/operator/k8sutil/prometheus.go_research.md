# sources/control-plane/rook/pkg/operator/k8sutil/prometheus.go

## Purpose
`prometheus.go` builds and reconciles Prometheus Operator `ServiceMonitor` resources for Rook metrics endpoints.

## Important APIs, Types, and Functions
`getMonitoringClient()` creates a Prometheus monitoring clientset from `clusterd.Context.KubeConfig`. `GetServiceMonitor()` returns a ServiceMonitor template with `team=rook`, namespace selector, `app` and `rook_cluster` match labels, one `/metrics` endpoint, `10s` interval, `HonorLabels`, and a relabel rule setting `cluster` to the namespace. `CreateOrUpdateServiceMonitor()` creates on not found or updates the existing spec and labels.

## Control Flow, State, and Persistence
The file persists state by creating or updating Kubernetes custom resources. On update, it retains the existing object metadata except labels and spec. It returns errors for client creation, get, create, and update failures.

## Dependencies and Integration Points
It depends on Prometheus Operator API/client packages, Rook `clusterd.Context`, Kubernetes API errors, and pointer helpers. It integrates Rook services with Prometheus scraping when the CRD/client is available.

## Risks
The client is constructed internally, making unit testing update paths harder. If the Prometheus CRD is absent or RBAC is missing, create/update fails. Only labels and spec are updated, so annotations or owner references from the desired definition are not reconciled.

## Test Signals
`prometheus_test.go` covers the static ServiceMonitor template. It does not cover client creation, create-or-update behavior, not-found branching, or error handling.
