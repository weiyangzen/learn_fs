# sources/cloud-native/moby/daemon/libnetwork/cmd/diagnostic/daemon.json

## Purpose
Provides a minimal daemon configuration for libnetwork diagnostic scenarios.

## Important APIs, Types, And Functions
The JSON enables `"debug": true` and sets `"network-diagnostic-port": 2000`.

## Control Flow
There is no executable flow. Docker daemon startup reads this file when used as configuration.

## State And Persistence
It configures daemon runtime behavior by enabling diagnostics on port 2000 and debug logging.

## Dependencies And Integration Points
Paired with the diagnostic command in the same folder, which defaults to port 2000 and calls diagnostic HTTP endpoints.

## Risks And Test Signals
Using this config in a real environment exposes diagnostics on a known port and increases logging verbosity. No tests are associated with the JSON itself.
