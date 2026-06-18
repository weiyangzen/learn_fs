# sources/cloud-native/moby/integration-cli/docker_cli_daemon_plugins_test.go

Purpose: Linux daemon tests for managed plugin lifecycle, plugin state restoration, live-restore behavior, volume plugin use, plugin filters, and plugin/volume references across restarts.

Important APIs/types/functions: methods on `DockerDaemonSuite`: `TestDaemonRestartWithPluginEnabled`, `TestDaemonRestartWithPluginDisabled`, `TestDaemonKillLiveRestoreWithPlugins`, `TestDaemonShutdownLiveRestoreWithPlugins`, `TestDaemonShutdownWithPlugins`, `TestDaemonKillWithPlugins`, `TestVolumePlugin`, `TestPluginVolumeRemoveOnRestart`, `TestPluginListFilterEnabled`, and `TestPluginListFilterCapability`.

Control flow: tests start an isolated daemon, install a known plugin image with permissions, optionally disabled, restart/kill/interrupt the daemon, and inspect `plugin ls` or host processes. Volume plugin tests create a plugin-backed volume, mount it into busybox, touch/list files, and remove the volume. Filter tests install disabled plugins and assert `plugin ls --filter` output.

State and persistence: plugin installation stores plugin metadata under daemon root and starts plugin processes. Enabled/disabled flags must persist across daemon restart. Volume references keep plugins in use until volumes are removed. Live-restore determines whether plugin processes survive daemon shutdown.

Dependencies and integration points: Linux build tag, amd64 and network requirements, daemon harness, external plugin image constants, `pgrep` for plugin processes, Unix signals, Docker plugin and volume CLIs.

Risks: network availability, architecture, and external plugin image availability affect reliability. Process-name matching with `pgrep -f` can be brittle. Cleanup must disable/remove plugins even after abnormal daemon termination.

Test signals: failures indicate broken plugin metadata restoration, incorrect live-restore process ownership, improper shutdown cleanup, plugin volume mount/remove issues, or bad plugin list filtering.
