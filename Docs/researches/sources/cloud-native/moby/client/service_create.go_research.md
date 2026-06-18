# sources/cloud-native/moby/client/service_create.go

## Purpose
`service_create.go` implements swarm service creation, including task spec validation, default image tagging, optional registry digest resolution, and warning aggregation.

## Important APIs, Types, And Functions
Types: `ServiceCreateOptions`, `ServiceCreateResult`. Functions: `ServiceCreate`, `resolveContainerSpecImage`, `resolvePluginSpecRemote`, `imageDigestAndPlatforms`, `imageWithDigestString`, `imageWithTagString`, `digestWarning`, `validateServiceSpec`. Important fields: `ServiceCreateOptions` has `Spec`, `EncodedRegistryAuth`, `QueryRegistry`; `ServiceCreateResult` has `ID`, `Warnings`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/services/create`; uses client helper(s) `post`. Image or plugin references are normalized before request construction, preventing malformed names from reaching the daemon.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `errors`, `fmt`, `net/http`, `strings`, `github.com/distribution/reference`, `github.com/moby/moby/api/types/registry`, `github.com/moby/moby/api/types/swarm`, `github.com/opencontainers/go-digest`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
malformed or schema-incompatible daemon JSON propagates as decode errors; callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
