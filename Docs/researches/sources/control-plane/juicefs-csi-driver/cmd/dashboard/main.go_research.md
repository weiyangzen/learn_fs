# sources/control-plane/juicefs-csi-driver/cmd/dashboard/main.go

## Purpose
This file is the main entrypoint for the JuiceFS CSI dashboard binary. It serves the dashboard API and optional static frontend, supports local dev kubeconfig, optional basic auth, optional controller-runtime manager support for cache/index resources, pprof, graceful shutdown, and version output.

## Important APIs, Types, and Functions
`main()` defines the Cobra command `juicefs-csi-dashboard`, registers `upgradeCmd`, reads `USERNAME`/`PASSWORD`, and defines persistent flags for version, port, dev mode, static dir, leader election, and manager enablement. `run()` resolves Kubernetes config, creates a controller-runtime manager or direct client, constructs `dashboard.NewAPI`, registers routes under `/api/v1`, serves static assets and SPA fallback, starts HTTP and pprof servers, and starts the dashboard manager when enabled. `getLocalConfig()` loads `$HOME/.kube/config`; `newManager()` creates the controller-runtime manager.

## Control Flow
The binary exits early for `--version`. Runtime namespace defaults to `kube-system` but can be overridden by `SYS_NAMESPACE`. In dev mode it uses local kubeconfig and enables permissive CORS; otherwise it uses in-cluster config and Gin release mode. Basic auth is installed only when both username and password are present. Static serving maps `/assets/...` to the dist assets and non-API fallback to `index.html`. Shutdown uses a two-signal flow: first signal triggers server shutdown; a second signal exits immediately.

## State and Persistence Behavior
The process stores runtime choices in `pkg/config` globals (`Namespace`, `DisableGraceUpgrade`, `DriverName`) and runs HTTP/manager goroutines. Persistent Kubernetes state is read/written by `pkg/dashboard` API handlers and optional manager controllers. It does not write local files.

## Dependencies and Integration Points
Dependencies include Gin, CORS middleware, Cobra, klog, controller-runtime, Kubernetes schemes, the cache-group-operator API scheme, `pkg/dashboard`, and `pkg/driver`. It integrates with `dashboard-ci.yaml`, dashboard image workflows, and `Makefile` dashboard targets.

## Risks
Basic auth is enabled only if both env vars are non-empty; missing one leaves the dashboard unauthenticated. The static `NoRoute` handler can call `c.File` twice for asset requests if the URI also is not `/api`, depending on Gin behavior after the first call. The pprof server logs errors but does not stop the main process. Metrics bind on `8082`, which can conflict with other managers in shared namespaces.

## Test Signals
Build and dashboard CI cover compilation and UI packaging indirectly. Runtime API behavior is likely covered by dashboard package tests or manual/E2E use, not by this file directly.
