# sources/cloud-native/soci-snapshotter/integration/startup_test.go

Purpose: validates snapshotter startup paths, containerd plugin registration, systemd socket activation, bad config failure, default config parsing, and config path handling.

Important APIs and flow: `TestSnapshotterStartup` starts containerd and SOCI with a Unix metrics socket colocated with the gRPC socket, then finds `io.containerd.snapshotter.v1 soci ok` in `ctr plugin ls`. `TestSnapshotterSystemdStartup` runs under systemd entrypoint and checks not-started timeout, socket-activated success, and direct start fallback while configured for socket activation. `TestSnapshotterStartupWithBadConfig` expects bad parallel pull chunk-size config to fail quickly. `TestStartWithDefaultConfig` boots with the repository example config. `TestStartWithConfigPaths` kills the daemon and manually starts it with default or explicit config paths, verifying missing explicit config fails and optional default config absence succeeds.

State and persistence: starts/stops containerd and snapshotter processes, manipulates config files, systemd units, sockets, and log monitors.

Dependencies and integration: uses systemd, containerd CLI, generated config TOML, log JSON parsing, test startup monitors, and snapshotter binary execution.

Risks and test signals: strong startup regression coverage. Systemd cases are skipped via `SKIP_SYSTEMD_TESTS`; timing uses short timeouts that can be flaky on slow hosts.
