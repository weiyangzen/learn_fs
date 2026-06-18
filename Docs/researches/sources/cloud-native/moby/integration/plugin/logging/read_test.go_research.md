# sources/cloud-native/moby/integration/plugin/logging/read_test.go

## Purpose
Tests container log reads when the selected logging plugin declares `ReadLogs: false`, verifying Docker's local log cache behavior and the `cache-disabled` log option.

## Important APIs, Types, And Functions
Uses the discard plugin, `PluginEnable`, daemon restart with optional `--log-opt=cache-disabled=...`, `ContainerCreate`, `ContainerStart`, `ContainerLogs`, `stdcopy.StdCopy`, and polling for container stop.

## Control Flow
The test builds/enables the discard log plugin, stops the daemon, then runs subtests for default cache, disabled cache, and explicitly enabled cache. Each subtest restarts daemon with options, creates an echo container using log driver `test`, waits for stop, then calls `ContainerLogs`. If caching is disabled, an error is expected; otherwise stdout must decode to `hello world`.

## State And Persistence Behavior
Plugin installation persists across daemon restarts. Container log availability depends on daemon log cache state, not plugin read support.

## Dependencies And Integration Points
Depends on non-Windows Unix socket plugins, daemon log cache implementation, plugin capability endpoint, stdcopy log framing, and container stop polling.

## Risks
Timeouts can occur if log stream EOF is delayed. The test reuses one API client across daemon restarts, so client/daemon reconnection behavior is part of the integration surface.

## Test Signals
Signals are expected `ContainerLogs` error when cache is disabled and decoded stdout exactly `hello world` when cache is available.
