# sources/control-plane/juicefs-csi-driver/cmd/main.go

## Purpose
This is the main entrypoint for the `juicefs-csi` binary. It defines CLI flags, handles version output, starts optional config reloading, probes bundled JuiceFS CLI versions, sets up signal handling, and dispatches to controller or node runtime based on the current pod name.

## Important APIs, Types, and Functions
Global variables hold CLI flag values for CSI endpoint, node id, format-in-pod, by-process mode, config path, controller features, node manager features, leader election, and logging. `main()` defines the Cobra command, registers flags, attaches klog flags, registers `upgradeCmd`, and executes. `run()` starts config reloading, probes CE/EE binary versions asynchronously, obtains a signal-aware context, and calls `controllerRun(ctx)` or `nodeRun(ctx)` based on `POD_NAME`.

## Control Flow
If `--version` is set, it prints `driver.GetVersionJSON()` and exits. If `--config` is provided, `config.StartConfigReloader` is started before runtime dispatch. A goroutine runs `juicefs version` commands for CE and EE binaries and records output in global config variables. The process then checks whether `POD_NAME` contains `csi-controller` or `csi-node` and invokes the matching run path.

## State and Persistence Behavior
The file mutates package-level config for built-in JuiceFS versions and starts a config reloader if requested. It does not persist files directly. All durable cluster state is managed by controller/node run paths and driver/controllers.

## Dependencies and Integration Points
It depends on Cobra, klog, controller-runtime logging/signal handling, `pkg/config`, `pkg/driver`, and `k8s.io/utils/exec`. It integrates with `cmd/controller.go`, the node runtime in another source file, and the upgrade command.

## Risks
Dispatch relies on `POD_NAME` string containment; if the binary is run outside the expected pod naming scheme, neither controller nor node path starts and the process exits after `run()` returns. The asynchronous version probe can race with code that reads `BuiltinCeVersion` or `BuiltinEeVersion` immediately after startup. Global CLI variables make isolated tests harder.

## Test Signals
Compilation is covered by `make` and CI. Runtime behavior is covered by E2E deployments that set `POD_NAME` through Kubernetes manifests and exercise controller/node modes.
