# sources/cloud-native/nydus/smoke/tests/takeover_test.go

## Purpose
This opt-in suite validates snapshotter-managed Nydus daemon recovery and hot upgrade while a container remains accessible. It covers daemon failover after kill, rolling upgrades caused by snapshotter restart, and snapshotter API-triggered daemon upgrade.

## Important APIs, Types, And Functions
Global state captures snapshotter name, test image, system socket, and candidate `nydusd` paths. `TakeoverTestSuit` stores context, converted test image, and `tool.SnapshotterClient`. `NewTakeoverTestSuit` prepares and converts the image. `TestFailover` runs a container, fetches daemon info, kills each daemon PID, waits, and checks workload access. `TestRestartSnapshotterHotUpgrade` alternates two `nydusd` paths in `/etc/nydus/config.toml` and restarts `nydus-snapshotter` repeatedly. `TestAPIHotUpgrade` sends an `UpgradeRequest` to the snapshotter system API. Helpers parse daemon version output, rewrite TOML config, remove containers/images, and check HTTP workload readiness.

## Control Flow
`TestTakeover` skips unless `TAKEOVER_TEST=true`, initializes defaults and paths, chmods the new daemon binary, creates the suite, and runs it synchronously. Each case starts the same converted image, perturbs daemon or snapshotter state, waits for recovery, and probes the workload URL.

## State And Persistence
The test mutates host state: it writes `/etc/nydus/config.toml`, restarts a systemd service, kills daemon PIDs, creates/removes containers, and pushes/removes images. Snapshotter daemon information is fetched from the configured Unix system socket.

## Dependencies And Integration Points
This depends on root permissions, systemd, nydus-snapshotter, containerd/nerdctl, `tool.SnapshotterClient`, `containerd/nydus-snapshotter/config`, and TOML marshaling. It exercises `/api/v1/daemons` and `/api/v1/daemons/upgrade` on the snapshotter controller.

## Risks
This is host-invasive and not safe for generic CI without isolation. The hard-coded default config path and `/usr/local/bin/nydusd` fallback are deployment-specific. Fixed five-second waits may be too short or unnecessarily long depending on host load.

## Test Signals
Signals are continued successful HTTP access to the workload after daemon kill, after repeated snapshotter restarts with alternating daemon paths, and after snapshotter upgrade API invocation.
