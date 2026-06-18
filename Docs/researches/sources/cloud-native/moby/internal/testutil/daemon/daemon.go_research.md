# sources/cloud-native/moby/internal/testutil/daemon/daemon.go

## Purpose
Core test harness for creating, starting, stopping, restarting, configuring, inspecting, and cleaning isolated `dockerd` processes used by integration tests.

## Important APIs, Types, And Functions
- `Daemon` stores root paths, socket paths, command/log handles, storage/userns/rootless options, Swarm options, extra environment, and cached info.
- Constructors `NewDaemon` and `New` create isolated folders, data roots, exec roots, socket roots, rootless runtime dirs, and apply `Option` values.
- Lifecycle methods `Start`, `StartWithError`, `StartWithLogFile`, `StartWithBusybox`, `Stop`, `StopWithError`, `Kill`, `Restart`, and `RestartWithError` manage the daemon process.
- Client/log helpers include `NewClient`, `NewClientT`, `ReadLogFile`, `TailLogs`, `ScanLogs`, and poll matchers.
- Configuration/introspection helpers include `BinaryPath`, `RootDir`, `Sock`, `Info`, `FirewallBackendDriver`, `FirewallReloadedAt`, `ReloadConfig`, `SetEnvVar`, `LoadImage`, `LoadBusybox`, `TamperWithContainerConfig`, and cleanup helpers.
- Path helpers `sanitizedTestName` and `sanitizePathComponent` make test names safe for filesystem/artifact tooling.

## Control Flow
Construction chooses a destination, creates directories, configures rootless ownership if needed, and stores options. `StartWithLogFile` assembles dockerd arguments, defaulting to debug mode and optionally applying storage/firewall/userns/experimental/init/rootless settings, starts the process, launches a wait goroutine, then polls `/_ping` until ready or timeout. Stop sends interrupt, waits, retries interrupts, and kills on timeout. Restart composes stop/start. Cleanup removes mounts, raft data, storage directories, and network namespaces.

## State And Persistence
The harness creates persistent-on-disk test state under the configured destination: daemon folder, `root`, `docker.log`, pid file, exec root, socket under `/tmp/docker-integration`, rootless XDG runtime dir, optional resolv.conf override, and daemon storage. `d.Root` may be updated after startup by querying `/info`, especially for user namespace remap.

## Dependencies And Integration Points
Integrates with OS process management, Unix/TLS sockets, Moby client, test request helpers, containerd namespace flags, dockerd command-line flags, OpenTelemetry environment, storage drivers, rootless `sudo`, and platform-specific signal/mount helpers.

## Risks And Edge Cases
Startup readiness depends on polling within 60 seconds. Rootless mode requires user/ownership setup and forbids non-default dockerd binaries. `SetEnvVar` has an index check that only replaces entries at index greater than zero, so an existing first entry is appended instead of replaced. Cleanup intentionally preserves logs for artifacts and may leave root folders. Direct config tampering assumes on-disk daemon layout.

## Test Signals
Strong signals are successful `/_ping`, successful `/info` root query, clean stop or kill fallback, readable logs, expected sanitized paths, image load into isolated daemon, and cleanup removing storage subdirectories without failing tests.
