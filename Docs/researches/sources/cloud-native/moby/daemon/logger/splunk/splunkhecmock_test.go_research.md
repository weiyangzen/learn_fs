# sources/cloud-native/moby/daemon/logger/splunk/splunkhecmock_test.go

## Purpose
This file implements a local HTTP Event Collector test server used by Splunk logger tests. It records incoming HEC messages, simulates server failure or blocking, validates request headers and paths, and decodes optional gzip bodies.

## Important APIs, Types, And Functions
`HTTPEventCollectorMock` owns a TCP listener, token, request counters, connection verification flag, gzip mode, recorded `splunkMessage` slice, and failure/blocking controls. `NewHTTPEventCollectorMock`, `Serve`, `Close`, `ServeHTTP`, `simulateErr`, and `withBlock` are the main helpers. `splunkMessage.EventAsString` and `EventAsMap` give typed assertions for raw and structured events.

## Control Flow
The mock listens on localhost port 0. `ServeHTTP` increments request count, snapshots failure/blocking state under a mutex, optionally blocks until context cancellation, returns 500 when simulating errors, accepts one `OPTIONS` verification request, and handles `POST` by validating HEC path and authorization. It determines gzip use from `Content-Encoding`, decompresses when needed, reads the body, splits adjacent JSON objects, unmarshals each into `splunkMessage`, and responds 200.

## State, Persistence, And Dependencies
All state is in-memory and test-scoped. The mutex protects toggled error/block settings but message appends and counters are otherwise used in single-test request flows. Dependencies are standard `net`, `net/http`, `compress/gzip`, `encoding/json`, `io`, `sync`, `testing`, and `time`.

## Integration Points
The mock is tightly coupled to Splunk driver test expectations: exact HEC event path, Splunk auth token format, single verification request, stable gzip choice per logger, and concatenated JSON event bodies.

## Risks And Edge Cases
The body splitter assumes adjacent JSON objects can be separated at `}{`, which is sufficient for current driver output but not a general JSON stream parser. `ServeHTTP` reads `hec.blockingCtx` after unlocking instead of the local `ctx` variable, so future mutation could surprise blocked-request tests. `Close` only closes the listener and does not gracefully shut down the HTTP server.

## Test Signals
This helper enables strong assertions in `splunk_test.go`: captured `messages`, `numOfRequests`, `connectionVerified`, `gzipEnabled`, injected 500 responses, and blocked endpoint behavior.
