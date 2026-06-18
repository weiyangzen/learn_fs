<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/node.go -->
# sources/control-plane/juicefs-csi-driver/cmd/node.go

## Purpose
`node.go` starts the JuiceFS CSI node service. It converts process flags and pod environment into `pkg/config` globals, starts pprof and Prometheus endpoints, optionally starts pod reconciliation, initializes graceful-upgrade file descriptor passing, and runs the CSI driver.

## Important APIs, Types, and Functions
The main entry points are `parseNodeConfig()` and `nodeRun(ctx)`. `parseNodeConfig` consumes environment variables such as `DRIVER_NAME`, `JUICEFS_IMMUTABLE`, `NODE_NAME`, `JUICEFS_MOUNT_NAMESPACE`, `POD_NAME`, mount image overrides, share-mount toggles, reconcile intervals, and `DISABLE_GRACE_UPGRADE`. It calls `k8s.NewClient()`, `GetPod`, `passfd.InitGlobalFds`, and `grace.ServeGfShutdown`. `nodeRun` registers Go metrics, creates `driver.NewDriver`, and calls `drv.Run()`.

## Control Flow, State, and Persistence
Configuration is stored by mutating package-level `config` variables. In process mode it exits early and avoids pod lookup. Otherwise it validates pod identity, reads the current CSI pod from Kubernetes, and starts graceful shutdown socket serving unless disabled. Runtime state is mostly in goroutines: pprof binds localhost from port 6060 upward, metrics binds `config.WebPort`, pod manager/reconciler may run in the background, and context cancellation stops the driver.

## Dependencies and Integration Points
This file connects CLI globals from the main package to Kubernetes clients, controller reconciliation, CSI driver construction, Prometheus, pprof, passfd/graceful upgrade, and image resolution utilities. It is deployment-sensitive because many behaviors are environment-driven by the node DaemonSet.

## Risks and Test Signals
Risks include fatal exits on missing pod metadata, ignored parse errors for duration values, unbounded pprof port retry loops, metrics bind conflicts, global mutable config, and graceful-upgrade socket startup failures blocking the node. Test signals are env-matrix unit tests around `parseNodeConfig`, node startup with and without kubelet access, metrics endpoint availability, graceful upgrade socket behavior, and integration tests that verify driver shutdown on context cancellation.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/node.go -->
