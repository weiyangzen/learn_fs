# sources/cloud-native/containerd/integration/release_upgrade_linux_test.go

## Purpose

`release_upgrade_linux_test.go` is a Linux integration suite that verifies containerd can upgrade from the latest supported 1.7 and 2.0 release binaries to the current tree while preserving CRI pod, container, image, shim, logging, and metric behavior. It starts real previous-release `containerd` processes against temporary root/state/config directories, prepares workloads through CRI, gracefully stops the old daemon, starts the current daemon on the same state, and then exercises recovery and mutation paths.

## Important APIs, Types, and Functions

- `TestUpgrade` drives version matrix coverage for `1.7` and `2.0`.
- `runUpgradeTestCase` and `runUpgradeTestCaseWithExistingConfig` own process lifecycle, config installation, cleanup, and repeated current-release restarts between verification callbacks.
- `upgradeVerifyCaseFunc`, `beforeUpgradeHookFunc`, and `setupUpgradeVerifyCase` model per-scenario setup, pre-upgrade hooks, and post-upgrade assertions.
- Scenario setup functions include `shouldRecoverAllThePodsAfterUpgrade`, `execToExistingContainer`, `shouldManipulateContainersInPodAfterUpgrade`, `shouldRecoverExistingImages`, `shouldParseMetricDataCorrectly`, and `shouldAdjustShimVersionDuringRestarting`.
- `podTCtx` wraps sandbox ID/config/runtime service and exposes `createContainer`, `containerDataDir`, `shimPid`, `dataDir`, `imageVolumeDir`, and `stop`.
- `ctrdProc` wraps a child `containerd` process and exposes CRI clients, paths, readiness polling, signal, wait, and log dumping helpers.
- Shim helpers read `bootstrap.json` or `address`, build ttrpc task clients, and check shim process shutdown after pod deletion.

## Control Flow

Each subtest downloads a previous-release binary set, writes an old config, starts previous `containerd`, waits for CRI readiness, prepares test pods/images/containers, stops the old process with `SIGTERM`, optionally runs a hook such as killing a shim, writes current config if needed, and starts the current `containerd`. Verification callbacks are run in order, and the daemon is restarted between callbacks to catch delayed recovery problems. Cleanup stops/removes pods and terminates the current daemon.

The scenario callbacks cover ready, created, exited, stopped, and killed-shim states. They verify CRI listing/status, container IO recovery, `ExecSync`, shim protocol version mismatch handling, creating/stopping/removing containers in recovered pods, data directory cleanup, image persistence, and parsing memory metrics from shims created by older releases.

## State and Persistence Behavior

Persistent state lives under the temp `root`, `state`, and CRI `rootDir` paths reused across old/current daemon restarts. The test intentionally inspects sandbox/container metadata directories, image volume directories, shim bundle files, CRI status `Info["config"]`, logs, image references, and shim sockets. It also checks that removing containers and sandboxes deletes the expected CRI directories and that existing image IDs survive upgrade.

## Dependencies and Integration Points

The file integrates with real `containerd` binaries, CRI runtime/image services from `integration/remote`, Kubernetes CRI API types, containerd task v2/v3 shim APIs, ttrpc, runtime namespaces, release config files, `images` fixtures, and Linux signals/process management. It depends on helpers from the wider integration package for CRI config builders, container options, failpoints, and image names.

## Risks and Edge Cases

The test is expensive and environment-sensitive: it downloads GitHub release artifacts, starts real daemons, uses Linux shims and sockets, sleeps for log/metric readiness, and relies on signal ordering. The shim version mismatch path is subtle because current shims may produce v3 bootstrap metadata while recovering v2 tasks. Cleanup is deliberately defensive because failed upgrades can leave running pods, mounts, sockets, and state directories.

## Test Signals

This file is itself a high-value integration signal for upgrade compatibility. Failures point to CRI state migration, shim reconnection, image store persistence, container IO restore, metric decoding, process lifecycle, or cleanup regressions across containerd releases.
