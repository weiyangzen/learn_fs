# sources/control-plane/juicefs-csi-driver/cmd/app/pod_manager.go

## Purpose
This file defines the node-side pod manager that watches Pods scheduled to the current node and wires the CSI node pod reconciler.

## Important APIs, Types, and Functions
`PodManager` holds a controller-runtime manager, project Kubernetes client, and uncached API reader. `NewPodManager()` creates a manager with metrics on `0.0.0.0:8082`, lease-based leader election ID `pod.juicefs.com`, and a Pod cache filtered by `spec.nodeName == config.NodeName`. `Start(ctx)` registers `mountctrl.NewPodController(m.client, m.cacheReader)` and starts the manager.

## Control Flow
Package `init()` registers core Kubernetes objects into the shared scheme. Construction gets in-cluster config, creates the manager with a filtered Pod cache, creates a `k8sclient.K8sClient`, and returns the manager wrapper. Start registers the pod controller, logs startup, and blocks on `mgr.Start(ctx)`.

## State and Persistence Behavior
The pod manager does not persist local state. It watches Pods assigned to a node and delegates reconciliation state to `PodController`, which is responsible for mount behavior and Kubernetes object changes.

## Dependencies and Integration Points
It depends on controller-runtime, Kubernetes schemes, the global `config.NodeName`, project controller package, and project k8s client. It is used by the CSI node command path when node pod management is enabled.

## Risks
If `config.NodeName` is empty or wrong, the cache will miss target pods and reconciliation will not occur. Metrics bind address `8082` overlaps with dashboard manager metrics if both run in the same network namespace. Leader election namespace is not explicitly set here, so cluster RBAC/namespace defaults matter.

## Test Signals
Coverage is primarily E2E: pod-mount, process, webhook, and mount-pod lifecycle tests depend on node-side pod reconciliation working.
