# sources/cloud-native/moby/client/ping.go

## Purpose
`ping.go` implements daemon reachability, capability header parsing, HEAD-to-GET fallback, and optional API-version negotiation.

## Important APIs, Types, And Functions
Types: `PingOptions`, `PingResult`, `SwarmStatus`. Functions: `Ping`, `ping`, `newPingResult`. Important fields: `PingOptions` has `NegotiateAPIVersion`, `ForceNegotiate`; `PingResult` has `APIVersion`, `OSType`, `Experimental`, `BuilderVersion`, `SwarmStatus`; `SwarmStatus` has `NodeState`, `ControlAvailable`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/`, `/_ping`; uses client helper(s) `buildRequest`, `doRequest`, `sendRequest`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `net/http`, `path`, `strings`, `github.com/moby/moby/api/types/build`, `github.com/moby/moby/api/types/swarm`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
