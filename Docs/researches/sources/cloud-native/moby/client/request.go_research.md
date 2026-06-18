# sources/cloud-native/moby/client/request.go

## Purpose
`request.go` is the HTTP transport core for the client package. It builds API-versioned requests, serializes JSON bodies, decorates connection errors, maps daemon HTTP errors to errdefs, and drains/ closes response bodies for reuse.

## Important APIs, Types, And Functions
Functions: `head`, `get`, `post`, `postRaw`, `put`, `putRaw`, `delete`, `prepareJSONRequest`, `buildRequest`, `sendRequest`, `doRequest`, `checkResponseErr`, `addHeaders`, `jsonEncode`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file uses client helper(s) `buildRequest`, `doRequest`, `putRaw`, `sendRequest`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `bytes`, `context`, `encoding/json`, `errors`, `fmt`, `io`, `net`, `net/http`, `net/url`, `os`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
malformed or schema-incompatible daemon JSON propagates as decode errors; callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
