# sources/control-plane/juicefs-csi-driver/cmd/dashboard/upgrade.go

## Purpose
This file implements the dashboard `upgrade` subcommand, which orchestrates smooth batch upgrades of JuiceFS mount pods by loading a batch config, triggering CSI node-side upgrade commands via Kubernetes exec, monitoring replacement pods, and writing upgrade status back to the batch config.

## Important APIs, Types, and Functions
`upgradeCmd` is the Cobra command. `BatchUpgrade` holds namespace, loaded `BatchConfig`, Kubernetes REST config/clientset/project client, grouped pod batches, status lock, per-pod status map, overall status, current/next batch status, and current batch index. `PodUpgrade` stores the original Pod, hash label, and upgrade UUID. Main methods are `Run`, `fetchPods`, `processBatch`, `triggerUpgrade`, `waitForUpgrade`, `flushStatus`, `handleSignal`, `panic`, and `Write`.

## Control Flow
The command refuses to run when `DISABLE_GRACE_UPGRADE=true`. It resolves namespace and Kubernetes config, creates clients, loads batch config from `common.JfsUpgradeConfig`, initializes every configured pod to pending, flushes status, fetches live mount pods, starts signal handling, and calls `Run`.

`Run` ticks once per second. It advances batches when the current batch is pending/success or failed with `IgnoreError`, stops on pause/stop/fail, and writes final success/failure status. `processBatch` groups current batch entries by CSI node pod, triggers one exec per CSI node, and waits for relevant mount pods on each node. `triggerUpgrade` runs `juicefs-csi-driver upgrade BATCH --batchConfig ... --batchIndex ...` inside the CSI node `juicefs-plugin` container over SPDY. `waitForUpgrade` watches mount pods on the target node, matches old/new pods by upgrade UUID, and marks pod success when a replacement is ready.

The `Write` method implements `io.Writer` for remote exec streams. It prints output and parses `POD-START`, `POD-SUCCESS`, and `POD-FAIL` messages with regexes to update per-pod status.

## State and Persistence Behavior
Upgrade status is persisted by `config.UpdateUpgradeConfig` back to the named upgrade ConfigMap. Runtime state is protected partly by `sync.Mutex`. The command also reacts to process signals: `SIGUSR1` toggles pause/resume and `SIGTERM` stops future batches.

## Dependencies and Integration Points
It depends on Gin for dev/release config behavior, Cobra, Kubernetes client-go REST/clientset/informers/remotecommand, controller-runtime config, project `common`, `config`, `k8sclient`, and `util/resource`. It integrates with CSI node pods that must support the internal `juicefs-csi-driver upgrade BATCH` command and emit parseable log markers.

## Risks
`setNextBatchStatus` writes without locking while other status fields are locked, so signal and ticker interactions can race. `processBatch` launches goroutines that close over loop variables without passing them as parameters; in Go versions with old loop semantics this would be a bug, and even with newer semantics care is needed around shared `u.crtBatch`. The command calls `os.Exit` in failure paths, limiting cleanup. Regex parsing of stream output is a brittle status channel. The 300-second wait is fixed and may be too short for large clusters.

## Test Signals
There are no direct tests in this file. Signals come from dashboard build, Go tests in related packages, and any manual/automated smooth-upgrade workflows that exercise batch ConfigMaps and CSI node exec.
