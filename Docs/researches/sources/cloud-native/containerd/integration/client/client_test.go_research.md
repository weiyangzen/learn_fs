# sources/cloud-native/containerd/integration/client/client_test.go

## Purpose
This file is the main integration harness and core client behavior test set for containerd.

## Important APIs, Types, and Functions
`TestMain` starts or connects to containerd, configures defaults, pulls a seed image, runs tests, and tears down. `newClient` centralizes client creation. Tests cover new client, image pull, discard-content unpack, all/some platform fetch, download concurrency, tracing, concurrent unpacks, reconnect, namespace default runtime labels, and runtime info.

## Control Flow
`TestMain` parses flags, requires root outside short mode, detects CRIU, starts a daemon unless `-no-daemon`, waits for readiness, logs version, sets namespace default snapshotter, pulls the seed image with unpack, runs the suite, then stops/kills the daemon and removes test root. Individual tests create clients and use `testContext`.

## State and Persistence
The daemon uses `defaultRoot` and `defaultState`; tests create content, images, snapshots, leases, namespace labels, and tracing spans. Cleanup removes test root when the dedicated daemon is used.

## Dependencies and Integration Points
Integrates the real client API, daemon process helper, defaults, images package, leases, content/image stores, namespaces, OpenTelemetry, platform matchers, and semaphore unpack limiter.

## Risks
Requires root, network/image availability, and stable registry behavior. Some tests skip in short mode or CI. The discard-content test depends on synchronous GC and correct snapshot retention.

## Test Signals
High-value end-to-end coverage for pull/fetch/unpack/content GC, tracing spans, reconnect, namespace labels, runtime feature reporting, and concurrency options.
