# sources/cloud-native/moby/integration/daemon/daemon_test.go

Purpose: cross-platform daemon integration tests for daemon ID/config validation, seccomp config loading, feature flags, proxy configuration and sanitization, and live-restore behavior.

Important APIs and helpers: `TestConfigDaemonID`, `TestDaemonConfigValidation`, `TestConfigDaemonSeccompProfiles`, `TestDaemonConfigFeatures`, `TestDaemonProxy`, `TestLiveRestore`, `testLiveRestoreAutoRemove`, `testLiveRestoreVolumeReferences`, and `testLiveRestoreUserChainsSetup`.

Control flow: config tests run sub-daemons or the daemon binary with validation flags and fixture JSON files. Feature tests alter daemon config and reload or restart to inspect advertised features. Proxy tests configure proxies by environment, command-line flags, and config file, use an HTTP test server to observe whether pulls route through the proxy, and assert credentials are masked in logs and conflict errors. Live-restore tests restart or stop daemons while containers keep running, then verify auto-remove cleanup, mounted volume/image reference protection, bind-mount handling, and Docker user iptables chain reinstallation.

State and persistence: tests exercise daemon root state, config files, log output, image/container/volume references across restarts, live container processes, mount reference counts, and proxy settings surfaced through `Info`. Live-restore cases explicitly validate state reconciliation after daemon restart.

Dependencies and integration: depends on daemon harness, internal container/process helpers, HTTP test servers, seccomp fixtures, filesystem temp dirs, volumes, mounts, iptables, and Moby client APIs. It integrates command-line flags, config-file parsing, SIGHUP reloads, logging, image pulls, volume/image reference accounting, and live-restore recovery.

Risks: sub-daemon tests are skipped or constrained on Windows/rootless/remote environments. Proxy tests rely on failed pulls still reaching expected hosts. Live-restore tests are timing-sensitive around process exit, mount namespaces, and daemon restart.

Test signals: broad daemon lifecycle signal for validation behavior, secure logging, proxy precedence, live-restore cleanup, reference accounting, and runtime state restoration after daemon downtime.
