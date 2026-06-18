# sources/control-plane/juicefs-csi-driver/cmd/controller.go

## Purpose
This file implements the CSI controller process path. It parses controller-related runtime configuration, starts optional controller-runtime managers, exposes metrics/pprof, and starts the CSI driver service.

## Important APIs, Types, and Functions
`parseControllerConfig()` maps Cobra flags and environment variables into `pkg/config` globals. `controllerRun(ctx)` calls the parser, starts pprof and Prometheus metrics HTTP servers, optionally starts `app.ControllerManager`, creates `driver.NewDriver(...)`, and runs it.

## Control Flow
`parseControllerConfig` sets process/webhook/provisioner/cache/validation flags, reads `DRIVER_NAME`, disables mount manager/webhook/provisioner in by-process mode, parses `JUICEFS_IMMUTABLE`, reads node/namespace/mount/config paths, resolves CE/EE mount images from specific or generic env vars, enables share-mount modes, parses provisioner worker threads, and when not in webhook sidecar mode attempts to inherit CSI node pod attributes by listing `app=juicefs-csi-node` Pods or falling back to the `juicefs-csi-node` DaemonSet template.

`controllerRun` requires `nodeID`, starts pprof on localhost starting at port 6060, starts `/metrics` on `config.WebPort`, launches `ControllerManager` when mount manager or webhook is enabled, then starts the CSI driver. It stops the driver when the context is cancelled.

## State and Persistence Behavior
The file writes configuration into global `pkg/config` variables. It starts HTTP servers and controller-runtime managers, creates Kubernetes clients, and reads live Pods/DaemonSets to populate `config.CSIPod`. Persistent cluster mutations are delegated to the CSI driver and controllers.

## Dependencies and Integration Points
It depends on Prometheus, Kubernetes API types, project `app`, `config`, `driver`, `k8sclient`, and `util.ImageResol`. It is selected from `cmd/main.go` when `POD_NAME` contains `csi-controller`.

## Risks
The pprof goroutine exits the process on the first `ListenAndServe` error inside an infinite loop, so the port-increment logic is effectively unreachable after failure. Many config values are global and process-wide, which complicates tests and concurrent modes. If no CSI node Pod or DaemonSet is found in non-webhook mode, the controller exits. Environment parsing failures are fatal.

## Test Signals
Go build covers compilation. E2E controller modes exercise provisioning, mount manager, webhook, metrics-adjacent startup, and config inheritance.
