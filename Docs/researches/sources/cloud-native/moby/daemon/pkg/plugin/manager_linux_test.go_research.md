<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager_linux_test.go -->
# sources/cloud-native/moby/daemon/pkg/plugin/manager_linux_test.go

## Purpose
Tests Linux plugin manager behavior around mounts, failed create cleanup, and already-running plugin restore.

## Important APIs, Types, And Functions
Tests use `TestManagerWithPluginMounts`, `newTestPlugin`, `simpleExecutor`, `TestCreateFailed`, `executorWithRunning`, `TestPluginAlreadyRunningOnStartup`, and `listenTestPlugin`.

## Control Flow
Root-only tests create temporary manager roots and fake plugins. One test mounts tmpfs under an enabled plugin and verifies removing another plugin does not unmount it. Create-failure test uses an executor returning an error. Startup test simulates an already-listening Unix socket and checks client setup with live-restore on/off.

## State, Dependencies, And Integration Points
Uses temp directories, real mounts, Unix sockets, and fake executors. It integrates manager reload/enable/remove paths with filesystem and mount behavior.

## Risks And Test Signals
Root requirements skip some coverage for unprivileged runs. Unix socket path length is explicitly managed. These tests are high-value lifecycle signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/pkg/plugin/manager_linux_test.go -->
