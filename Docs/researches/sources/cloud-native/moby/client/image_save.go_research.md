# sources/cloud-native/moby/client/image_save.go

## Purpose
`image_save.go` downloads one or more daemon images as a tar stream, optionally constrained by platform for multi-platform images.

## Important APIs, Types, And Functions
Types: `ImageSaveResult`, `imageSaveResult`. Functions: `ImageSave`. Important fields: `imageSaveResult` has `io.ReadCloser`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/images/get`; uses client helper(s) `get`. It gates newer options through `requiresVersion`, so callers get an explicit client-side error before sending unsupported parameters to older daemons.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `io`, `net/url`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks; version-gated parameters can fail against older daemons.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
