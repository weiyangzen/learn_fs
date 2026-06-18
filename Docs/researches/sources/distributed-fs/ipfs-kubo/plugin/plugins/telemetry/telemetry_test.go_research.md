<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/telemetry/telemetry_test.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/telemetry/telemetry_test.go

## Purpose

This file integration-tests telemetry send behavior against a local HTTP server and a real temporary Kubo repo.

## Important APIs, Types, and Functions

`mockServer` returns an `httptest.Server` that requires POST `/`, JSON content type, non-empty body, unmarshals `LogEvent`, and exposes the received event. `makeNode` creates a temp fsrepo using pebbleds, registers the pebbleds datastore parser, initializes config, opens the repo, builds an online node with nil routing, and marks it daemon. `TestSendTelemetry` initializes a `telemetryPlugin` with `runOnce`, overrides endpoint to the test server, starts it, and checks UUID equality.

## Control Flow, State, and Integration

The test writes a real repo and datastore under temp paths, starts a real core node, and performs an actual HTTP POST to the test server. It does not wait for timers because `runOnce` bypasses delay.

## Dependencies, Risks, and Test Signals

Dependencies include httptest, pebbleds, fsrepo, config, core node construction, and nil libp2p routing. It signals that telemetry can collect and send without crashing, but does not cover opt-out removal, failed HTTP status, delay scheduling, or platform detection branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/telemetry/telemetry_test.go -->
