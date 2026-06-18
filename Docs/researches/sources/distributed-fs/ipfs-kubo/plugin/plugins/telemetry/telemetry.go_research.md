<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/telemetry/telemetry.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/telemetry/telemetry.go

## Purpose

This daemon-internal plugin collects anonymized Kubo usage/configuration telemetry and periodically sends it to a configured HTTP endpoint, with opt-out and delayed first send semantics.

## Important APIs, Types, and Functions

`LogEvent` defines the JSON payload: UUID, agent version, private network, bootstrap customization, repo size and uptime buckets, routing/provide/autonat/autoconf/swarm/autotls/discovery/platform fields. `telemetryPlugin` stores mode, endpoint, UUID filename, send delay, node/config/event, and start time. `Init` reads mode/delay/endpoint from env/config, handles opt-out UUID removal, and defaults to on/auto. `loadUUID` reads or creates repo-local `telemetry_uuid`. `Start` validates daemon/online mode, loads UUID, shows opt-in info in auto mode, and schedules sends. `prepareEvent` calls collectors, platform detection is cached, and `sendTelemetry` posts JSON with a 30-second HTTP timeout.

## Control Flow, State, and Integration

The plugin is initialized before node start, then started with direct `IpfsNode`. In production it waits `sendDelay` before first send, then repeats every 24 hours. In tests `runOnce` sends immediately. Persistent state is the UUID file in the repo, removed on opt-out. Collection reads repo config, repo size, swarm addresses, private network key, peer host reachability, runtime OS/arch, and host/container/VM indicators.

## Dependencies, Risks, and Test Signals

Dependencies include HTTP, JSON, uuid, Kubo config/core/corerepo, libp2p network/pnet/multiaddr, runtime OS files under `/proc` and `/sys`, and environment variables. Risks include privacy-sensitive field creep, endpoint failures, UUID persistence after config changes, goroutine timer leaks only ending with process, false container/VM detection, repo-size cost, and Unicode console output. `telemetry_test.go` verifies immediate send to a mock server and UUID round-trip; more tests would be useful for opt-out, delay parsing, bucketing, and platform detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/telemetry/telemetry.go -->
