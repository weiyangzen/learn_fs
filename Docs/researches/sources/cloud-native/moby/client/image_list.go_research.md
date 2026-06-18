# sources/cloud-native/moby/client/image_list.go

## Purpose
`image_list.go` implements the Moby client surface for image list. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Functions: `ImageList`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/images/json`; uses client helper(s) `get`. It gates newer options through `requiresVersion`, so callers get an explicit client-side error before sending unsupported parameters to older daemons.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `net/url`, `github.com/moby/moby/api/types/image`, `github.com/moby/moby/client/pkg/versions`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
malformed or schema-incompatible daemon JSON propagates as decode errors; callers must close returned streams or consume iterator helpers to avoid response leaks; version-gated parameters can fail against older daemons.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
