<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/upgrade.go -->
# sources/control-plane/juicefs-csi-driver/cmd/upgrade.go

## Purpose
`upgrade.go` defines the `upgrade` Cobra command used to trigger smooth mount-pod upgrades through the node-side graceful shutdown socket.

## Important APIs, Types, and Functions
The file declares global command flags `recreate`, `batchConfigName`, and `crtBatchIndex`, plus `upgradeCmd`. The command checks `DISABLE_GRACE_UPGRADE`, validates an argument, and calls either `grace.TriggerBatchUpgrade(config.ShutdownSockPath, batchConfigName, crtBatchIndex)` for the sentinel pod name `BATCH`, or `grace.TriggerShutdown(config.ShutdownSockPath, name, recreate)` for a single mount pod. `init()` binds `--recreate`, `--batchConfig`, and `--batchIndex`.

## Control Flow, State, and Persistence
The command is synchronous and process-scoped. It derives behavior from environment, CLI args, and flags, then exits nonzero on disabled mode, missing target, or grace API error. Persistent effects are external: the grace socket recipient initiates mount pod shutdown/recreate or batch progress, while this command only reports success/failure.

## Dependencies and Integration Points
It integrates the CLI layer with `pkg/fuse/grace` and shared `pkg/config`. It must match the socket path served by the node process in `node.go` and the batch upgrade job logic that passes `BATCH`, config name, and batch index.

## Risks and Test Signals
Risks include the magic `BATCH` argument, absence of flag validation for batch config/index, reliance on shared socket path defaults, and hard process exits that complicate unit testing. Useful tests cover disabled grace mode, missing args, single-pod recreate/non-recreate calls, batch calls, and socket error propagation.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/cmd/upgrade.go -->
