# subset-b-000166 research

This grouped report covers the requested Moby client image, network, node, plugin, secret, request, and utility files. Each section is wrapped with source-path markers for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_import_test.go -->
# sources/cloud-native/moby/client/image_import_test.go

## Purpose
`image_import_test.go` tests the Moby client behavior for image import.

## Important APIs, Types, And Functions
Test functions: `TestImageImportError`, `TestImageImport`. Referenced routes or paths: `/images/create`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_import_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_inspect.go -->
# sources/cloud-native/moby/client/image_inspect.go

## Purpose
`image_inspect.go` implements the Moby client surface for image inspect. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Functions: `ImageInspect`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/images/`, `/json`; uses client helper(s) `get`. It gates newer options through `requiresVersion`, so callers get an explicit client-side error before sending unsupported parameters to older daemons.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `bytes`, `context`, `encoding/json`, `fmt`, `io`, `net/url`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks; version-gated parameters can fail against older daemons.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_inspect_opts.go -->
# sources/cloud-native/moby/client/image_inspect_opts.go

## Purpose
`image_inspect_opts.go` defines the option/result data contract used by the matching client API wrapper. It keeps public request options separate from private API serialization structs where functional options are needed.

## Important APIs, Types, And Functions
Types: `ImageInspectOption`, `imageInspectOptionFunc`, `imageInspectOpts`, `imageInspectOptions`, `ImageInspectResult`. Option helpers: `Apply`, `ImageInspectWithRawResponse`, `ImageInspectWithManifests`, `ImageInspectWithPlatform`. Fields: `imageInspectOpts` includes `raw`, `apiOptions`; `imageInspectOptions` includes `Manifests`, `Platform`; `ImageInspectResult` includes `image.InspectResponse`.

## Control Flow
The file has little runtime flow beyond `Apply` methods or option constructors. The endpoint implementation consumes these values, converts them into query parameters or headers, and leaves validation such as platform encoding or version checks to the API method.

## State And Persistence
Options are per-call value state and are not persisted. Result structs mirror daemon API response JSON and become durable only insofar as they describe daemon-side resources.

## Dependencies And Integration Points
The definitions integrate with the adjacent endpoint file and the Moby API model packages. Platform-aware options use OCI platform types and shared platform encoding helpers.

## Risks
Compatibility risk is in preserving exported field names and JSON tags, because downstream clients use these structs directly. Functional options must copy caller intent without hidden shared mutable state.

## Test Signals
Behavior is covered indirectly by the matching endpoint tests, which verify query serialization, response decoding, and version checks for options such as quiet, platform, filters, prune filters, and auth fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_inspect_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_inspect_test.go -->
# sources/cloud-native/moby/client/image_inspect_test.go

## Purpose
`image_inspect_test.go` tests the Moby client behavior for image inspect.

## Important APIs, Types, And Functions
Test functions: `TestImageInspectError`, `TestImageInspectImageNotFound`, `TestImageInspectWithEmptyID`, `TestImageInspect`, `TestImageInspectWithPlatform`. Referenced routes or paths: `/images/image_id/json`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_list.go -->
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
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_list_opts.go -->
# sources/cloud-native/moby/client/image_list_opts.go

## Purpose
`image_list_opts.go` defines the option/result data contract used by the matching client API wrapper. It keeps public request options separate from private API serialization structs where functional options are needed.

## Important APIs, Types, And Functions
Types: `ImageListOptions`, `ImageListResult`. Fields: `ImageListOptions` includes `All`, `Filters`, `SharedSize`, `Manifests`, `Identity`; `ImageListResult` includes `Items`.

## Control Flow
The file has little runtime flow beyond `Apply` methods or option constructors. The endpoint implementation consumes these values, converts them into query parameters or headers, and leaves validation such as platform encoding or version checks to the API method.

## State And Persistence
Options are per-call value state and are not persisted. Result structs mirror daemon API response JSON and become durable only insofar as they describe daemon-side resources.

## Dependencies And Integration Points
The definitions integrate with the adjacent endpoint file and the Moby API model packages. Platform-aware options use OCI platform types and shared platform encoding helpers.

## Risks
Compatibility risk is in preserving exported field names and JSON tags, because downstream clients use these structs directly. Functional options must copy caller intent without hidden shared mutable state.

## Test Signals
Behavior is covered indirectly by the matching endpoint tests, which verify query serialization, response decoding, and version checks for options such as quiet, platform, filters, prune filters, and auth fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_list_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_list_test.go -->
# sources/cloud-native/moby/client/image_list_test.go

## Purpose
`image_list_test.go` tests the Moby client behavior for image list.

## Important APIs, Types, And Functions
Test functions: `TestImageListError`, `TestImageListConnectionError`, `TestImageList`. Referenced routes or paths: `/images/json`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_load.go -->
# sources/cloud-native/moby/client/image_load.go

## Purpose
`image_load.go` uploads a tar stream to the daemon's image load endpoint and returns a cancel-aware reader for daemon progress/output.

## Important APIs, Types, And Functions
Types: `ImageLoadResult`, `imageLoadResult`. Functions: `ImageLoad`. Important fields: `imageLoadResult` has `io.ReadCloser`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/images/load`; uses client helper(s) `postRaw`. It gates newer options through `requiresVersion`, so callers get an explicit client-side error before sending unsupported parameters to older daemons.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `io`, `net/http`, `net/url`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks; version-gated parameters can fail against older daemons.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_load.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_load_opts.go -->
# sources/cloud-native/moby/client/image_load_opts.go

## Purpose
`image_load_opts.go` defines the option/result data contract used by the matching client API wrapper. It keeps public request options separate from private API serialization structs where functional options are needed.

## Important APIs, Types, And Functions
Types: `ImageLoadOption`, `imageLoadOptionFunc`, `imageLoadOpts`, `imageLoadOptions`. Option helpers: `Apply`, `ImageLoadWithQuiet`, `ImageLoadWithPlatforms`. Fields: `imageLoadOpts` includes `apiOptions`; `imageLoadOptions` includes `Quiet`, `Platforms`.

## Control Flow
The file has little runtime flow beyond `Apply` methods or option constructors. The endpoint implementation consumes these values, converts them into query parameters or headers, and leaves validation such as platform encoding or version checks to the API method.

## State And Persistence
Options are per-call value state and are not persisted. Result structs mirror daemon API response JSON and become durable only insofar as they describe daemon-side resources.

## Dependencies And Integration Points
The definitions integrate with the adjacent endpoint file and the Moby API model packages. Platform-aware options use OCI platform types and shared platform encoding helpers.

## Risks
Compatibility risk is in preserving exported field names and JSON tags, because downstream clients use these structs directly. Functional options must copy caller intent without hidden shared mutable state.

## Test Signals
Behavior is covered indirectly by the matching endpoint tests, which verify query serialization, response decoding, and version checks for options such as quiet, platform, filters, prune filters, and auth fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_load_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_load_test.go -->
# sources/cloud-native/moby/client/image_load_test.go

## Purpose
`image_load_test.go` tests the Moby client behavior for image load.

## Important APIs, Types, And Functions
Test functions: `TestImageLoadError`, `TestImageLoad`. Referenced routes or paths: `/images/load`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_load_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_prune.go -->
# sources/cloud-native/moby/client/image_prune.go

## Purpose
`image_prune.go` implements the Moby client surface for image prune. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `ImagePruneOptions`, `ImagePruneResult`. Functions: `ImagePrune`. Important fields: `ImagePruneOptions` has `Filters`; `ImagePruneResult` has `Report`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/images/prune`; uses client helper(s) `post`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `fmt`, `net/url`, `github.com/moby/moby/api/types/image`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
malformed or schema-incompatible daemon JSON propagates as decode errors; callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_prune.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_prune_test.go -->
# sources/cloud-native/moby/client/image_prune_test.go

## Purpose
`image_prune_test.go` tests the Moby client behavior for image prune.

## Important APIs, Types, And Functions
Test functions: `TestImagePruneError`, `TestImagePrune`. Referenced routes or paths: `/images/prune`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_prune_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_pull.go -->
# sources/cloud-native/moby/client/image_pull.go

## Purpose
`image_pull.go` implements registry image pull support and exposes a streaming `ImagePullResponse` that can be read directly, iterated as JSON progress messages, or waited on until completion.

## Important APIs, Types, And Functions
Types: `ImagePullResponse`. Functions: `ImagePull`, `getAPITagFromNamedRef`, `tryImageCreate`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/images/create`; uses client helper(s) `post`. Unauthorized registry responses can trigger a caller-provided privilege callback and one retry with refreshed `X-Registry-Auth`. Image or plugin references are normalized before request construction, preventing malformed names from reaching the daemon.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `io`, `iter`, `net/http`, `net/url`, `github.com/containerd/errdefs`, `github.com/distribution/reference`, `github.com/moby/moby/api/types/jsonstream`, `github.com/moby/moby/api/types/registry`, `github.com/moby/moby/client/internal`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks; auth retry paths must close failed responses and preserve the refreshed header.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_pull.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_pull_opts.go -->
# sources/cloud-native/moby/client/image_pull_opts.go

## Purpose
`image_pull_opts.go` defines the option/result data contract used by the matching client API wrapper. It keeps public request options separate from private API serialization structs where functional options are needed.

## Important APIs, Types, And Functions
Types: `ImagePullOptions`. Fields: `ImagePullOptions` includes `All`, `RegistryAuth`, `PrivilegeFunc`, `Platforms`.

## Control Flow
The file has little runtime flow beyond `Apply` methods or option constructors. The endpoint implementation consumes these values, converts them into query parameters or headers, and leaves validation such as platform encoding or version checks to the API method.

## State And Persistence
Options are per-call value state and are not persisted. Result structs mirror daemon API response JSON and become durable only insofar as they describe daemon-side resources.

## Dependencies And Integration Points
The definitions integrate with the adjacent endpoint file and the Moby API model packages. Platform-aware options use OCI platform types and shared platform encoding helpers.

## Risks
Compatibility risk is in preserving exported field names and JSON tags, because downstream clients use these structs directly. Functional options must copy caller intent without hidden shared mutable state.

## Test Signals
Behavior is covered indirectly by the matching endpoint tests, which verify query serialization, response decoding, and version checks for options such as quiet, platform, filters, prune filters, and auth fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_pull_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_pull_test.go -->
# sources/cloud-native/moby/client/image_pull_test.go

## Purpose
`image_pull_test.go` tests the Moby client behavior for image pull.

## Important APIs, Types, And Functions
Test functions: `TestImagePullReferenceParseError`, `TestImagePullAnyError`, `TestImagePullStatusUnauthorizedError`, `TestImagePullWithUnauthorizedErrorAndPrivilegeFuncError`, `TestImagePullWithUnauthorizedErrorAndAnotherUnauthorizedError`, `TestImagePullWithPrivilegedFuncNoError`, `TestImagePullWithoutErrors`, `TestImagePullResponse`. Referenced routes or paths: `/images/create`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_pull_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_push.go -->
# sources/cloud-native/moby/client/image_push.go

## Purpose
`image_push.go` implements registry image push support with tag/platform query handling, authentication retry, and a streaming JSON-message response.

## Important APIs, Types, And Functions
Types: `ImagePushResponse`. Functions: `ImagePush`, `tryImagePush`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/images/`, `/push`; uses client helper(s) `post`. It gates newer options through `requiresVersion`, so callers get an explicit client-side error before sending unsupported parameters to older daemons. Unauthorized registry responses can trigger a caller-provided privilege callback and one retry with refreshed `X-Registry-Auth`. Image or plugin references are normalized before request construction, preventing malformed names from reaching the daemon.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `errors`, `fmt`, `io`, `iter`, `net/http`, `net/url`, `github.com/containerd/errdefs`, `github.com/distribution/reference`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks; version-gated parameters can fail against older daemons; auth retry paths must close failed responses and preserve the refreshed header.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_push.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_push_opts.go -->
# sources/cloud-native/moby/client/image_push_opts.go

## Purpose
`image_push_opts.go` defines the option/result data contract used by the matching client API wrapper. It keeps public request options separate from private API serialization structs where functional options are needed.

## Important APIs, Types, And Functions
Types: `ImagePushOptions`. Fields: `ImagePushOptions` includes `All`, `RegistryAuth`, `PrivilegeFunc`, `Platform`.

## Control Flow
The file has little runtime flow beyond `Apply` methods or option constructors. The endpoint implementation consumes these values, converts them into query parameters or headers, and leaves validation such as platform encoding or version checks to the API method.

## State And Persistence
Options are per-call value state and are not persisted. Result structs mirror daemon API response JSON and become durable only insofar as they describe daemon-side resources.

## Dependencies And Integration Points
The definitions integrate with the adjacent endpoint file and the Moby API model packages. Platform-aware options use OCI platform types and shared platform encoding helpers.

## Risks
Compatibility risk is in preserving exported field names and JSON tags, because downstream clients use these structs directly. Functional options must copy caller intent without hidden shared mutable state.

## Test Signals
Behavior is covered indirectly by the matching endpoint tests, which verify query serialization, response decoding, and version checks for options such as quiet, platform, filters, prune filters, and auth fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_push_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_push_test.go -->
# sources/cloud-native/moby/client/image_push_test.go

## Purpose
`image_push_test.go` tests the Moby client behavior for image push.

## Important APIs, Types, And Functions
Test functions: `TestImagePushReferenceError`, `TestImagePushAnyError`, `TestImagePushStatusUnauthorizedError`, `TestImagePushWithUnauthorizedErrorAndPrivilegeFuncError`, `TestImagePushWithUnauthorizedErrorAndAnotherUnauthorizedError`, `TestImagePushWithPrivilegedFuncNoError`, `TestImagePushWithoutErrors`. Referenced routes or paths: `/images/%s/push`, `/images/docker.io/myname/myimage/push`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_push_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_remove.go -->
# sources/cloud-native/moby/client/image_remove.go

## Purpose
`image_remove.go` implements the Moby client surface for image remove. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Functions: `ImageRemove`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/images/`; uses client helper(s) `delete`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `net/url`, `github.com/moby/moby/api/types/image`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
malformed or schema-incompatible daemon JSON propagates as decode errors; callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_remove_opts.go -->
# sources/cloud-native/moby/client/image_remove_opts.go

## Purpose
`image_remove_opts.go` defines the option/result data contract used by the matching client API wrapper. It keeps public request options separate from private API serialization structs where functional options are needed.

## Important APIs, Types, And Functions
Types: `ImageRemoveOptions`, `ImageRemoveResult`. Fields: `ImageRemoveOptions` includes `Platforms`, `Force`, `PruneChildren`; `ImageRemoveResult` includes `Items`.

## Control Flow
The file has little runtime flow beyond `Apply` methods or option constructors. The endpoint implementation consumes these values, converts them into query parameters or headers, and leaves validation such as platform encoding or version checks to the API method.

## State And Persistence
Options are per-call value state and are not persisted. Result structs mirror daemon API response JSON and become durable only insofar as they describe daemon-side resources.

## Dependencies And Integration Points
The definitions integrate with the adjacent endpoint file and the Moby API model packages. Platform-aware options use OCI platform types and shared platform encoding helpers.

## Risks
Compatibility risk is in preserving exported field names and JSON tags, because downstream clients use these structs directly. Functional options must copy caller intent without hidden shared mutable state.

## Test Signals
Behavior is covered indirectly by the matching endpoint tests, which verify query serialization, response decoding, and version checks for options such as quiet, platform, filters, prune filters, and auth fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_remove_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_remove_test.go -->
# sources/cloud-native/moby/client/image_remove_test.go

## Purpose
`image_remove_test.go` tests the Moby client behavior for image remove.

## Important APIs, Types, And Functions
Test functions: `TestImageRemoveError`, `TestImageRemoveImageNotFound`, `TestImageRemove`. Referenced routes or paths: `/images/image_id`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_save.go -->
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
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_save.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_save_opts.go -->
# sources/cloud-native/moby/client/image_save_opts.go

## Purpose
`image_save_opts.go` defines the option/result data contract used by the matching client API wrapper. It keeps public request options separate from private API serialization structs where functional options are needed.

## Important APIs, Types, And Functions
Types: `ImageSaveOption`, `imageSaveOptionFunc`, `imageSaveOpts`, `imageSaveOptions`. Option helpers: `Apply`, `ImageSaveWithPlatforms`. Fields: `imageSaveOpts` includes `apiOptions`; `imageSaveOptions` includes `Platforms`.

## Control Flow
The file has little runtime flow beyond `Apply` methods or option constructors. The endpoint implementation consumes these values, converts them into query parameters or headers, and leaves validation such as platform encoding or version checks to the API method.

## State And Persistence
Options are per-call value state and are not persisted. Result structs mirror daemon API response JSON and become durable only insofar as they describe daemon-side resources.

## Dependencies And Integration Points
The definitions integrate with the adjacent endpoint file and the Moby API model packages. Platform-aware options use OCI platform types and shared platform encoding helpers.

## Risks
Compatibility risk is in preserving exported field names and JSON tags, because downstream clients use these structs directly. Functional options must copy caller intent without hidden shared mutable state.

## Test Signals
Behavior is covered indirectly by the matching endpoint tests, which verify query serialization, response decoding, and version checks for options such as quiet, platform, filters, prune filters, and auth fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_save_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_save_test.go -->
# sources/cloud-native/moby/client/image_save_test.go

## Purpose
`image_save_test.go` tests the Moby client behavior for image save.

## Important APIs, Types, And Functions
Test functions: `TestImageSaveError`, `TestImageSave`. Referenced routes or paths: `/images/get`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_save_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_search.go -->
# sources/cloud-native/moby/client/image_search.go

## Purpose
`image_search.go` implements the Moby client surface for image search. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Functions: `ImageSearch`, `tryImageSearch`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/images/search`; uses client helper(s) `get`. Unauthorized registry responses can trigger a caller-provided privilege callback and one retry with refreshed `X-Registry-Auth`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `net/http`, `net/url`, `strconv`, `github.com/containerd/errdefs`, `github.com/moby/moby/api/types/registry`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
malformed or schema-incompatible daemon JSON propagates as decode errors; callers must close returned streams or consume iterator helpers to avoid response leaks; auth retry paths must close failed responses and preserve the refreshed header.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_search.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_search_opts.go -->
# sources/cloud-native/moby/client/image_search_opts.go

## Purpose
`image_search_opts.go` defines the option/result data contract used by the matching client API wrapper. It keeps public request options separate from private API serialization structs where functional options are needed.

## Important APIs, Types, And Functions
Types: `ImageSearchResult`, `ImageSearchOptions`. Fields: `ImageSearchResult` includes `Items`; `ImageSearchOptions` includes `RegistryAuth`, `PrivilegeFunc`, `Filters`, `Limit`.

## Control Flow
The file has little runtime flow beyond `Apply` methods or option constructors. The endpoint implementation consumes these values, converts them into query parameters or headers, and leaves validation such as platform encoding or version checks to the API method.

## State And Persistence
Options are per-call value state and are not persisted. Result structs mirror daemon API response JSON and become durable only insofar as they describe daemon-side resources.

## Dependencies And Integration Points
The definitions integrate with the adjacent endpoint file and the Moby API model packages. Platform-aware options use OCI platform types and shared platform encoding helpers.

## Risks
Compatibility risk is in preserving exported field names and JSON tags, because downstream clients use these structs directly. Functional options must copy caller intent without hidden shared mutable state.

## Test Signals
Behavior is covered indirectly by the matching endpoint tests, which verify query serialization, response decoding, and version checks for options such as quiet, platform, filters, prune filters, and auth fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_search_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_search_test.go -->
# sources/cloud-native/moby/client/image_search_test.go

## Purpose
`image_search_test.go` tests the Moby client behavior for image search.

## Important APIs, Types, And Functions
Test functions: `TestImageSearchAnyError`, `TestImageSearchStatusUnauthorizedError`, `TestImageSearchWithUnauthorizedErrorAndPrivilegeFuncError`, `TestImageSearchWithUnauthorizedErrorAndAnotherUnauthorizedError`, `TestImageSearchWithPrivilegedFuncNoError`, `TestImageSearchWithoutErrors`. Referenced routes or paths: `/images/search`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_search_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_tag.go -->
# sources/cloud-native/moby/client/image_tag.go

## Purpose
`image_tag.go` implements the Moby client surface for image tag. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `ImageTagOptions`, `ImageTagResult`. Functions: `ImageTag`. Important fields: `ImageTagOptions` has `Source`, `Target`; `ImageTagResult` has `}`, `func`, `source`, `target`, `if`, `return`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/images/`, `/tag`; uses client helper(s) `post`. Image or plugin references are normalized before request construction, preventing malformed names from reaching the daemon.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `errors`, `fmt`, `net/url`, `github.com/distribution/reference`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_tag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/image_tag_test.go -->
# sources/cloud-native/moby/client/image_tag_test.go

## Purpose
`image_tag_test.go` tests the Moby client behavior for image tag.

## Important APIs, Types, And Functions
Test functions: `TestImageTagError`, `TestImageTagInvalidReference`, `TestImageTagInvalidSourceImageName`, `TestImageTagHexSource`, `TestImageTag`. Referenced routes or paths: `/images/image_id/tag`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/image_tag_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/a/example_test.go -->
# sources/cloud-native/moby/client/internal/gofix/a/example_test.go

## Purpose
`example_test.go` tests the Moby client behavior for example. These files are compile-only examples for Go fix directives rather than runtime daemon tests.

## Important APIs, Types, And Functions
Test functions: none exported; package documentation/example file. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/a/example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/b/example_test.go -->
# sources/cloud-native/moby/client/internal/gofix/b/example_test.go

## Purpose
`example_test.go` tests the Moby client behavior for example. These files are compile-only examples for Go fix directives rather than runtime daemon tests.

## Important APIs, Types, And Functions
Test functions: none exported; package documentation/example file. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/b/example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/c/example_test.go -->
# sources/cloud-native/moby/client/internal/gofix/c/example_test.go

## Purpose
`example_test.go` tests the Moby client behavior for example. These files are compile-only examples for Go fix directives rather than runtime daemon tests.

## Important APIs, Types, And Functions
Test functions: none exported; package documentation/example file. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/c/example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/d/example_test.go -->
# sources/cloud-native/moby/client/internal/gofix/d/example_test.go

## Purpose
`example_test.go` tests the Moby client behavior for example. These files are compile-only examples for Go fix directives rather than runtime daemon tests.

## Important APIs, Types, And Functions
Test functions: none exported; package documentation/example file. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/d/example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/doc_test.go -->
# sources/cloud-native/moby/client/internal/gofix/doc_test.go

## Purpose
`doc_test.go` tests the Moby client behavior for doc. These files are compile-only examples for Go fix directives rather than runtime daemon tests.

## Important APIs, Types, And Functions
Test functions: none exported; package documentation/example file. Referenced routes or paths: `//go:fix replace`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/doc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/e/example_test.go -->
# sources/cloud-native/moby/client/internal/gofix/e/example_test.go

## Purpose
`example_test.go` tests the Moby client behavior for example. These files are compile-only examples for Go fix directives rather than runtime daemon tests.

## Important APIs, Types, And Functions
Test functions: none exported; package documentation/example file. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/e/example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/f/example_test.go -->
# sources/cloud-native/moby/client/internal/gofix/f/example_test.go

## Purpose
`example_test.go` tests the Moby client behavior for example. These files are compile-only examples for Go fix directives rather than runtime daemon tests.

## Important APIs, Types, And Functions
Test functions: none exported; package documentation/example file. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/f/example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/g/example1_test.go -->
# sources/cloud-native/moby/client/internal/gofix/g/example1_test.go

## Purpose
`example1_test.go` tests the Moby client behavior for example1. These files are compile-only examples for Go fix directives rather than runtime daemon tests.

## Important APIs, Types, And Functions
Test functions: none exported; package documentation/example file. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/g/example1_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/g/example2_test.go -->
# sources/cloud-native/moby/client/internal/gofix/g/example2_test.go

## Purpose
`example2_test.go` tests the Moby client behavior for example2. These files are compile-only examples for Go fix directives rather than runtime daemon tests.

## Important APIs, Types, And Functions
Test functions: none exported; package documentation/example file. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/g/example2_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/h/example_test.go -->
# sources/cloud-native/moby/client/internal/gofix/h/example_test.go

## Purpose
`example_test.go` tests the Moby client behavior for example. These files are compile-only examples for Go fix directives rather than runtime daemon tests.

## Important APIs, Types, And Functions
Test functions: none exported; package documentation/example file. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/h/example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/i/example_test.go -->
# sources/cloud-native/moby/client/internal/gofix/i/example_test.go

## Purpose
`example_test.go` tests the Moby client behavior for example. These files are compile-only examples for Go fix directives rather than runtime daemon tests.

## Important APIs, Types, And Functions
Test functions: none exported; package documentation/example file. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/i/example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/j/example_test.go -->
# sources/cloud-native/moby/client/internal/gofix/j/example_test.go

## Purpose
`example_test.go` tests the Moby client behavior for example. These files are compile-only examples for Go fix directives rather than runtime daemon tests.

## Important APIs, Types, And Functions
Test functions: none exported; package documentation/example file. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/j/example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/k/example1_test.go -->
# sources/cloud-native/moby/client/internal/gofix/k/example1_test.go

## Purpose
`example1_test.go` tests the Moby client behavior for example1. These files are compile-only examples for Go fix directives rather than runtime daemon tests.

## Important APIs, Types, And Functions
Test functions: none exported; package documentation/example file. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/k/example1_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/k/example2_test.go -->
# sources/cloud-native/moby/client/internal/gofix/k/example2_test.go

## Purpose
`example2_test.go` tests the Moby client behavior for example2. These files are compile-only examples for Go fix directives rather than runtime daemon tests.

## Important APIs, Types, And Functions
Test functions: none exported; package documentation/example file. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/gofix/k/example2_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/json-stream.go -->
# sources/cloud-native/moby/client/internal/json-stream.go

## Purpose
`json-stream.go` selects the correct decoder for Docker JSON stream media types and provides an RS-filtering reader for RFC 7464 JSON text sequences.

## Important APIs, Types, And Functions
Types: `DecoderFn`, `rsFilterReader`. Functions: `NewJSONStreamDecoder`, `NewRSFilterReader`, `Read`.

## Control Flow
`NewJSONStreamDecoder` wraps JSON sequence input with `NewRSFilterReader`; the reader repeatedly strips ASCII RS bytes, avoids returning `(0, nil)` after consuming separators, and preserves EOF semantics when filtered data remains.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `encoding/json`, `io`, `slices`, `github.com/moby/moby/api/types`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
Filtering mutates the read buffer slice in place, so callers rely on standard `io.Reader` ownership rules. A bug here would break pull/push progress decoding for JSON sequence responses.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/json-stream.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/json-stream_test.go -->
# sources/cloud-native/moby/client/internal/json-stream_test.go

## Purpose
`json-stream_test.go` tests the Moby client behavior for json-stream.

## Important APIs, Types, And Functions
Test functions: `TestJSONStreamDecode_JSONSequence`, `TestRSFilterReader_SkipsRSOnlyRead`, `TestRSFilterReader_SkipsRSBeforeEOF`. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/json-stream_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/jsonmessages.go -->
# sources/cloud-native/moby/client/internal/jsonmessages.go

## Purpose
`jsonmessages.go` wraps a daemon JSON-message response body as an `io.ReadCloser`, an iterator of `jsonstream.Message`, and a blocking `Wait` helper.

## Important APIs, Types, And Functions
Types: `Stream`, `httpError`. Functions: `NewJSONMessageStream`, `Read`, `Close`, `JSONMessages`, `Wait`, `Error`, `Unwrap`, `Is`, `httpErrorFromStatusCode`.

## Control Flow
`JSONMessages` registers a context cancellation callback that closes the body, decodes messages until EOF/error, suppresses decode noise when the context is canceled, and always closes once. `Wait` returns the first transport/decode/context error or message-level daemon error mapped through HTTP errdefs.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `errors`, `io`, `iter`, `sync`, `github.com/containerd/errdefs/pkg/errhttp`, `github.com/moby/moby/api/types/jsonstream`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
The nil-reader constructor panics by design. Iterator users must respect context cancellation and message errors; incorrect status-code mapping would break callers checking errdefs.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/jsonmessages.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/jsonmessages_test.go -->
# sources/cloud-native/moby/client/internal/jsonmessages_test.go

## Purpose
`jsonmessages_test.go` tests the Moby client behavior for jsonmessages.

## Important APIs, Types, And Functions
Test functions: `TestStreamWait`, `TestStreamWait_ContextCanceled`. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/jsonmessages_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/mod/mod.go -->
# sources/cloud-native/moby/client/internal/mod/mod.go

## Purpose
`mod.go` extracts a display-friendly module version from Go build info without importing `golang.org/x/mod`.

## Important APIs, Types, And Functions
Types: none. Functions: `Version`, `moduleVersion`, `getVersion`, `normalize`, `splitMetadata`, `splitPseudo`, `isTimestamp`, `parseSemVer`.

## Control Flow
`Version` reads build info once, searches main and dependency modules, prefers replacement versions when present, drops devel/empty values, strips selected metadata, and normalizes pseudo-versions by preserving base version and truncating revisions.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `fmt`, `runtime/debug`, `strconv`, `strings`, `sync`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
Pseudo-version parsing intentionally implements only recognized Go forms; unrecognized semver variants fall back to the original base. This is for display, not ordering.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/mod/mod.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/mod/mod_test.go -->
# sources/cloud-native/moby/client/internal/mod/mod_test.go

## Purpose
`mod_test.go` tests the Moby client behavior for mod.

## Important APIs, Types, And Functions
Test functions: `TestModuleVersion`. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/mod/mod_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/timestamp/timestamp.go -->
# sources/cloud-native/moby/client/internal/timestamp/timestamp.go

## Purpose
`timestamp.go` parses CLI-style time filters for logs/events into daemon timestamp strings and splits daemon timestamp strings into seconds/nanoseconds.

## Important APIs, Types, And Functions
Types: none. Functions: `GetTimestamp`, `ParseTimestamps`, `parseTimestamp`.

## Control Flow
`GetTimestamp` tries duration-relative-to-reference first, then RFC3339/local date layouts chosen from input shape, then Unix timestamp validation. `ParseTimestamps` handles empty defaults and fractional nanoseconds.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `fmt`, `math`, `strconv`, `strings`, `time`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
Local timezone behavior depends on the reference time zone. Fractional nanosecond scaling uses float math and truncates based on digit length, so long fractions deserve regression coverage.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/timestamp/timestamp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/internal/timestamp/timestamp_test.go -->
# sources/cloud-native/moby/client/internal/timestamp/timestamp_test.go

## Purpose
`timestamp_test.go` tests the Moby client behavior for timestamp.

## Important APIs, Types, And Functions
Test functions: `TestGetTimestamp`, `TestParseTimestamps`. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/internal/timestamp/timestamp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/login.go -->
# sources/cloud-native/moby/client/login.go

## Purpose
`login.go` implements registry authentication through the daemon `/auth` endpoint and returns registry status/identity data.

## Important APIs, Types, And Functions
Types: `RegistryLoginOptions`, `RegistryLoginResult`. Functions: `RegistryLogin`. Important fields: `RegistryLoginOptions` has `Username`, `Password`, `ServerAddress`, `IdentityToken`, `RegistryToken`; `RegistryLoginResult` has `Auth`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/auth`; uses client helper(s) `post`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `net/url`, `github.com/moby/moby/api/types/registry`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
malformed or schema-incompatible daemon JSON propagates as decode errors; callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/login.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/network_connect.go -->
# sources/cloud-native/moby/client/network_connect.go

## Purpose
`network_connect.go` implements the Moby client surface for network connect. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `NetworkConnectOptions`, `NetworkConnectResult`. Functions: `NetworkConnect`. Important fields: `NetworkConnectOptions` has `Container`, `EndpointConfig`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/connect`, `/networks/`; uses client helper(s) `post`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `github.com/moby/moby/api/types/network`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/network_connect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/network_connect_test.go -->
# sources/cloud-native/moby/client/network_connect_test.go

## Purpose
`network_connect_test.go` tests the Moby client behavior for network connect.

## Important APIs, Types, And Functions
Test functions: `TestNetworkConnectError`, `TestNetworkConnectEmptyNilEndpointSettings`, `TestNetworkConnect`. Referenced routes or paths: `/networks/network_id/connect`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/network_connect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/network_create.go -->
# sources/cloud-native/moby/client/network_create.go

## Purpose
`network_create.go` implements the Moby client surface for network create. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `NetworkCreateOptions`, `NetworkCreateResult`. Functions: `NetworkCreate`. Important fields: `NetworkCreateOptions` has `Driver`, `Scope`, `EnableIPv4`, `EnableIPv6`, `IPAM`, `Internal`; `NetworkCreateResult` has `ID`, `Warning`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/networks/create`; uses client helper(s) `post`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `github.com/moby/moby/api/types/network`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
malformed or schema-incompatible daemon JSON propagates as decode errors; callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/network_create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/network_create_test.go -->
# sources/cloud-native/moby/client/network_create_test.go

## Purpose
`network_create_test.go` tests the Moby client behavior for network create.

## Important APIs, Types, And Functions
Test functions: `TestNetworkCreateError`, `TestNetworkCreateConnectionError`, `TestNetworkCreate`. Referenced routes or paths: `/networks/create`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/network_create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/network_disconnect.go -->
# sources/cloud-native/moby/client/network_disconnect.go

## Purpose
`network_disconnect.go` implements the Moby client surface for network disconnect. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `NetworkDisconnectOptions`, `NetworkDisconnectResult`. Functions: `NetworkDisconnect`. Important fields: `NetworkDisconnectOptions` has `Container`, `Force`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/disconnect`, `/networks/`; uses client helper(s) `post`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `github.com/moby/moby/api/types/network`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/network_disconnect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/network_disconnect_test.go -->
# sources/cloud-native/moby/client/network_disconnect_test.go

## Purpose
`network_disconnect_test.go` tests the Moby client behavior for network disconnect.

## Important APIs, Types, And Functions
Test functions: `TestNetworkDisconnectError`, `TestNetworkDisconnect`. Referenced routes or paths: `/networks/network_id/disconnect`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/network_disconnect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/network_inspect.go -->
# sources/cloud-native/moby/client/network_inspect.go

## Purpose
`network_inspect.go` implements the Moby client surface for network inspect. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `NetworkInspectResult`. Functions: `NetworkInspect`. Important fields: `NetworkInspectResult` has `Network`, `Raw`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/networks/`; uses client helper(s) `get`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `net/url`, `github.com/moby/moby/api/types/network`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
most risk sits in route/query compatibility and correct response body closure.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/network_inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/network_inspect_opts.go -->
# sources/cloud-native/moby/client/network_inspect_opts.go

## Purpose
`network_inspect_opts.go` defines the option/result data contract used by the matching client API wrapper. It keeps public request options separate from private API serialization structs where functional options are needed.

## Important APIs, Types, And Functions
Types: `NetworkInspectOptions`. Fields: `NetworkInspectOptions` includes `Scope`, `Verbose`.

## Control Flow
The file has little runtime flow beyond `Apply` methods or option constructors. The endpoint implementation consumes these values, converts them into query parameters or headers, and leaves validation such as platform encoding or version checks to the API method.

## State And Persistence
Options are per-call value state and are not persisted. Result structs mirror daemon API response JSON and become durable only insofar as they describe daemon-side resources.

## Dependencies And Integration Points
The definitions integrate with the adjacent endpoint file and the Moby API model packages. Platform-aware options use OCI platform types and shared platform encoding helpers.

## Risks
Compatibility risk is in preserving exported field names and JSON tags, because downstream clients use these structs directly. Functional options must copy caller intent without hidden shared mutable state.

## Test Signals
Behavior is covered indirectly by the matching endpoint tests, which verify query serialization, response decoding, and version checks for options such as quiet, platform, filters, prune filters, and auth fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/network_inspect_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/network_inspect_test.go -->
# sources/cloud-native/moby/client/network_inspect_test.go

## Purpose
`network_inspect_test.go` tests the Moby client behavior for network inspect.

## Important APIs, Types, And Functions
Test functions: `TestNetworkInspect`. Referenced routes or paths: `/networks/`, `/networks/network_id`, `/networks/test-500-response`, `/networks/unknown`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/network_inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/network_list.go -->
# sources/cloud-native/moby/client/network_list.go

## Purpose
`network_list.go` implements the Moby client surface for network list. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `NetworkListResult`. Functions: `NetworkList`. Important fields: `NetworkListResult` has `Items`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/networks`; uses client helper(s) `get`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `net/url`, `github.com/moby/moby/api/types/network`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
malformed or schema-incompatible daemon JSON propagates as decode errors; callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/network_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/network_list_opts.go -->
# sources/cloud-native/moby/client/network_list_opts.go

## Purpose
`network_list_opts.go` defines the option/result data contract used by the matching client API wrapper. It keeps public request options separate from private API serialization structs where functional options are needed.

## Important APIs, Types, And Functions
Types: `NetworkListOptions`. Fields: `NetworkListOptions` includes `Filters`.

## Control Flow
The file has little runtime flow beyond `Apply` methods or option constructors. The endpoint implementation consumes these values, converts them into query parameters or headers, and leaves validation such as platform encoding or version checks to the API method.

## State And Persistence
Options are per-call value state and are not persisted. Result structs mirror daemon API response JSON and become durable only insofar as they describe daemon-side resources.

## Dependencies And Integration Points
The definitions integrate with the adjacent endpoint file and the Moby API model packages. Platform-aware options use OCI platform types and shared platform encoding helpers.

## Risks
Compatibility risk is in preserving exported field names and JSON tags, because downstream clients use these structs directly. Functional options must copy caller intent without hidden shared mutable state.

## Test Signals
Behavior is covered indirectly by the matching endpoint tests, which verify query serialization, response decoding, and version checks for options such as quiet, platform, filters, prune filters, and auth fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/network_list_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/network_list_test.go -->
# sources/cloud-native/moby/client/network_list_test.go

## Purpose
`network_list_test.go` tests the Moby client behavior for network list.

## Important APIs, Types, And Functions
Test functions: `TestNetworkListError`, `TestNetworkList`. Referenced routes or paths: `/networks`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/network_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/network_prune.go -->
# sources/cloud-native/moby/client/network_prune.go

## Purpose
`network_prune.go` implements the Moby client surface for network prune. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `NetworkPruneOptions`, `NetworkPruneResult`. Functions: `NetworkPrune`. Important fields: `NetworkPruneOptions` has `Filters`; `NetworkPruneResult` has `Report`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/networks/prune`; uses client helper(s) `post`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `fmt`, `net/url`, `github.com/moby/moby/api/types/network`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
malformed or schema-incompatible daemon JSON propagates as decode errors; callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/network_prune.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/network_prune_test.go -->
# sources/cloud-native/moby/client/network_prune_test.go

## Purpose
`network_prune_test.go` tests the Moby client behavior for network prune.

## Important APIs, Types, And Functions
Test functions: `TestNetworkPruneError`, `TestNetworkPrune`. Referenced routes or paths: `/networks/prune`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/network_prune_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/network_remove.go -->
# sources/cloud-native/moby/client/network_remove.go

## Purpose
`network_remove.go` implements the Moby client surface for network remove. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `NetworkRemoveOptions`, `NetworkRemoveResult`. Functions: `NetworkRemove`. Important fields: .

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/networks/`; uses client helper(s) `delete`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/network_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/network_remove_test.go -->
# sources/cloud-native/moby/client/network_remove_test.go

## Purpose
`network_remove_test.go` tests the Moby client behavior for network remove.

## Important APIs, Types, And Functions
Test functions: `TestNetworkRemoveError`, `TestNetworkRemove`. Referenced routes or paths: `/networks/network_id`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/network_remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/node_inspect.go -->
# sources/cloud-native/moby/client/node_inspect.go

## Purpose
`node_inspect.go` implements the Moby client surface for node inspect. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `NodeInspectOptions`, `NodeInspectResult`. Functions: `NodeInspect`. Important fields: `NodeInspectOptions` has `}`, `type`, `Node`, `Raw`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/nodes/`; uses client helper(s) `get`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `bytes`, `context`, `encoding/json`, `io`, `github.com/moby/moby/api/types/swarm`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
malformed or schema-incompatible daemon JSON propagates as decode errors; callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/node_inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/node_inspect_test.go -->
# sources/cloud-native/moby/client/node_inspect_test.go

## Purpose
`node_inspect_test.go` tests the Moby client behavior for node inspect.

## Important APIs, Types, And Functions
Test functions: `TestNodeInspectError`, `TestNodeInspectNodeNotFound`, `TestNodeInspectWithEmptyID`, `TestNodeInspect`. Referenced routes or paths: `/nodes/node_id`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/node_inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/node_list.go -->
# sources/cloud-native/moby/client/node_list.go

## Purpose
`node_list.go` implements the Moby client surface for node list. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `NodeListOptions`, `NodeListResult`. Functions: `NodeList`. Important fields: `NodeListOptions` has `Filters`; `NodeListResult` has `Items`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/nodes`; uses client helper(s) `get`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `net/url`, `github.com/moby/moby/api/types/swarm`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
malformed or schema-incompatible daemon JSON propagates as decode errors; callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/node_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/node_list_test.go -->
# sources/cloud-native/moby/client/node_list_test.go

## Purpose
`node_list_test.go` tests the Moby client behavior for node list.

## Important APIs, Types, And Functions
Test functions: `TestNodeListError`, `TestNodeList`. Referenced routes or paths: `/nodes`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/node_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/node_remove.go -->
# sources/cloud-native/moby/client/node_remove.go

## Purpose
`node_remove.go` implements the Moby client surface for node remove. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `NodeRemoveOptions`, `NodeRemoveResult`. Functions: `NodeRemove`. Important fields: `NodeRemoveOptions` has `Force`; `NodeRemoveResult` has `}`, `func`, `nodeID,`, `if`, `return`, `}`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/nodes/`; uses client helper(s) `delete`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `net/url`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/node_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/node_remove_test.go -->
# sources/cloud-native/moby/client/node_remove_test.go

## Purpose
`node_remove_test.go` tests the Moby client behavior for node remove.

## Important APIs, Types, And Functions
Test functions: `TestNodeRemoveError`, `TestNodeRemove`. Referenced routes or paths: `/nodes/node_id`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/node_remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/node_update.go -->
# sources/cloud-native/moby/client/node_update.go

## Purpose
`node_update.go` implements the Moby client surface for node update. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `NodeUpdateOptions`, `NodeUpdateResult`. Functions: `NodeUpdate`. Important fields: `NodeUpdateOptions` has `Version`, `Spec`; `NodeUpdateResult` has `}`, `func`, `nodeID,`, `if`, `return`, `}`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/nodes/`, `/update`; uses client helper(s) `post`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `net/url`, `github.com/moby/moby/api/types/swarm`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/node_update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/node_update_test.go -->
# sources/cloud-native/moby/client/node_update_test.go

## Purpose
`node_update_test.go` tests the Moby client behavior for node update.

## Important APIs, Types, And Functions
Test functions: `TestNodeUpdateError`, `TestNodeUpdate`. Referenced routes or paths: `/nodes/node_id/update`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/node_update_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/ping.go -->
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
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/ping.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/ping_test.go -->
# sources/cloud-native/moby/client/ping_test.go

## Purpose
`ping_test.go` tests the Moby client behavior for ping.

## Important APIs, Types, And Functions
Test functions: `TestPingFail`, `TestPingWithError`, `TestPingSuccess`, `TestPingHeadFallback`. Referenced routes or paths: `/_ping`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/ping_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/jsonmessage/jsonmessage.go -->
# sources/cloud-native/moby/client/pkg/jsonmessage/jsonmessage.go

## Purpose
`jsonmessage.go` renders daemon JSON progress messages to terminals or plain streams, including progress bars, aux callbacks, line clearing, and compatibility wrappers.

## Important APIs, Types, And Functions
Types: `DisplayOpt`, `displayOpts`, `JSONMessagesStream`. Functions: `WithAuxCallback`, `RenderTUIProgress`, `clearLine`, `cursorUp`, `cursorDown`, `Display`, `DisplayJSONMessagesStream`, `DisplayStream`, `displayJSONMessagesStream`, `DisplayJSONMessages`, `DisplayMessages`, `displayJSONMessages`.

## Control Flow
Display functions decode messages or consume iterators, route aux messages to callbacks, render status/progress/error records, and use terminal cursor movement only when terminal mode is enabled.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `encoding/json`, `errors`, `fmt`, `io`, `iter`, `strings`, `time`, `github.com/docker/go-units`, `github.com/moby/moby/api/types/jsonstream`, `github.com/moby/term`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
Terminal control sequences and progress width calculations are easy to regress. Error messages embedded in JSON stream records must stop display with useful errors.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/jsonmessage/jsonmessage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/jsonmessage/jsonmessage_test.go -->
# sources/cloud-native/moby/client/pkg/jsonmessage/jsonmessage_test.go

## Purpose
`jsonmessage_test.go` tests the Moby client behavior for jsonmessage.

## Important APIs, Types, And Functions
Test functions: `TestRenderTUIProgress`, `TestDisplay`, `TestDisplayWithJSONError`, `TestDisplayStreamInvalidJSON`, `TestDisplayJSONMessagesStream`. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/jsonmessage/jsonmessage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/progress/progress.go -->
# sources/cloud-native/moby/client/pkg/progress/progress.go

## Purpose
`progress.go` defines the small progress event model and output abstraction shared by stream formatters and progress readers.

## Important APIs, Types, And Functions
Types: `Progress`, `Output`, `chanOutput`, `discardOutput`. Functions: `WriteProgress`, `ChanOutput`, `WriteProgress`, `DiscardOutput`, `Update`, `Updatef`, `Message`, `Messagef`, `Aux`.

## Control Flow
Helper functions construct `Progress` values for status, formatted messages, and aux payloads, then send them to an `Output` implementation such as channel output or discard output.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `fmt`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
The abstraction is intentionally tiny; downstream formatters rely on stable field meaning for ID, action, current, total, message, error, and aux.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/progress/progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/progress/progressreader.go -->
# sources/cloud-native/moby/client/pkg/progress/progressreader.go

## Purpose
`progressreader.go` wraps an `io.ReadCloser` and emits progress updates as bytes are read or when closed early.

## Important APIs, Types, And Functions
Types: `Reader`. Functions: `NewProgressReader`, `Read`, `Close`, `updateProgress`.

## Control Flow
`Read` increments the current byte count and emits updates; `Close` emits a final update when the stream ended early, then closes the underlying reader.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `io`, `time`, `golang.org/x/time/rate`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
Premature close semantics matter for upload progress; double-close and final-update behavior must stay stable.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/progress/progressreader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/progress/progressreader_test.go -->
# sources/cloud-native/moby/client/pkg/progress/progressreader_test.go

## Purpose
`progressreader_test.go` tests the Moby client behavior for progressreader.

## Important APIs, Types, And Functions
Test functions: `TestOutputOnPrematureClose`, `TestCompleteSilently`. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/progress/progressreader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/security/security_opts.go -->
# sources/cloud-native/moby/client/pkg/security/security_opts.go

## Purpose
`security_opts.go` defines the option/result data contract used by the matching client API wrapper. It keeps public request options separate from private API serialization structs where functional options are needed.

## Important APIs, Types, And Functions
Types: `Option`, `KeyValue`. Option helpers: `DecodeOptions`. Fields: `Option` includes `Name`, `Options`; `KeyValue` includes `Key,`.

## Control Flow
The file has little runtime flow beyond `Apply` methods or option constructors. The endpoint implementation consumes these values, converts them into query parameters or headers, and leaves validation such as platform encoding or version checks to the API method.

## State And Persistence
Options are per-call value state and are not persisted. Result structs mirror daemon API response JSON and become durable only insofar as they describe daemon-side resources.

## Dependencies And Integration Points
The definitions integrate with the adjacent endpoint file and the Moby API model packages. Platform-aware options use OCI platform types and shared platform encoding helpers.

## Risks
Compatibility risk is in preserving exported field names and JSON tags, because downstream clients use these structs directly. Functional options must copy caller intent without hidden shared mutable state.

## Test Signals
Behavior is covered indirectly by the matching endpoint tests, which verify query serialization, response decoding, and version checks for options such as quiet, platform, filters, prune filters, and auth fields.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/security/security_opts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/security/security_opts_test.go -->
# sources/cloud-native/moby/client/pkg/security/security_opts_test.go

## Purpose
`security_opts_test.go` tests the Moby client behavior for security opts.

## Important APIs, Types, And Functions
Test functions: `TestDecode`, `BenchmarkDecode`, `BenchmarkDecodeComplex`. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/security/security_opts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/streamformatter/streamformatter.go -->
# sources/cloud-native/moby/client/pkg/streamformatter/streamformatter.go

## Purpose
`streamformatter.go` formats progress events as either human-readable raw text or JSON messages for Docker stream output.

## Important APIs, Types, And Functions
Types: `jsonProgressFormatter`, `rawProgressFormatter`, `formatProgress`, `progressOutput`. Functions: `appendNewline`, `format`, `emptyMessage`, `formatStatus`, `formatProgress`, `format`, `emptyMessage`, `rawProgressString`, `formatProgress`, `NewProgressOutput`, `NewJSONProgressOutput`, `WriteProgress`.

## Control Flow
Formatter implementations convert `progress.Progress` into status lines, progress bars, aux JSON, or newline-delimited JSON. `progressOutput.WriteProgress` serializes access with a mutex before writing to the destination.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `encoding/json`, `fmt`, `io`, `strings`, `sync`, `time`, `github.com/docker/go-units`, `github.com/moby/moby/api/types/jsonstream`, `github.com/moby/moby/client/pkg/progress`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
Concurrent writes require locking; raw progress math must avoid divide-by-zero and terminal-width artifacts. JSON output must keep daemon-compatible field names.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/streamformatter/streamformatter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/streamformatter/streamformatter_test.go -->
# sources/cloud-native/moby/client/pkg/streamformatter/streamformatter_test.go

## Purpose
`streamformatter_test.go` tests the Moby client behavior for streamformatter.

## Important APIs, Types, And Functions
Test functions: `TestRawProgressFormatterFormatStatus`, `TestRawProgressFormatterFormatProgress`, `TestJSONProgressFormatterFormatProgress`, `TestJSONProgressFormatterFormatStatus`, `TestJSONProgressOutputWriteProgress`. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/streamformatter/streamformatter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/stringid/stringid.go -->
# sources/cloud-native/moby/client/pkg/stringid/stringid.go

## Purpose
`stringid.go` provides short ID truncation and random identifier generation utilities.

## Important APIs, Types, And Functions
Types: none. Functions: `TruncateID`, `GenerateRandomID`.

## Control Flow
`TruncateID` strips known digest prefixes and returns a short prefix; `GenerateRandomID` creates cryptographically random bytes, hex encodes them, and avoids all-numeric prefixes by regenerating.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `crypto/rand`, `encoding/hex`, `strings`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
Random generation can fail or loop in rare cases; truncation rules are user-visible in CLI output.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/stringid/stringid.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/stringid/stringid_test.go -->
# sources/cloud-native/moby/client/pkg/stringid/stringid_test.go

## Purpose
`stringid_test.go` tests the Moby client behavior for stringid.

## Important APIs, Types, And Functions
Test functions: `TestGenerateRandomID`, `TestTruncateID`. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/stringid/stringid_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/versions/compare.go -->
# sources/cloud-native/moby/client/pkg/versions/compare.go

## Purpose
`compare.go` compares dotted API/version strings numerically segment-by-segment.

## Important APIs, Types, And Functions
Types: none. Functions: `compare`, `LessThan`, `LessThanOrEqualTo`, `GreaterThan`, `GreaterThanOrEqualTo`, `Equal`.

## Control Flow
`compare` splits version strings on dots, parses numeric components, and exposes boolean helpers for less-than/equal/greater-than comparisons.

## State And Persistence
Utility state is in-memory only. Stream helpers own or close wrapped readers; progress and formatter helpers emit transient events; module/timestamp helpers return strings and do not persist data.

## Dependencies And Integration Points
Dependencies include `strconv`, `strings`. Integration points are the image push/pull/load/save streams, CLI display paths, API-version/user-agent code, and option parsing paths.

## Risks
Non-numeric segments parse as zero-like failures depending on `strconv.Atoi`; this helper is suited to Docker API version strings, not general semantic versioning.

## Test Signals
Companion tests cover sequence decoding, cancellation and close behavior, version normalization cases, timestamp formats, progress output, security option parsing, stream formatting, string ID generation/truncation, and numeric version comparison.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/versions/compare.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/versions/compare_test.go -->
# sources/cloud-native/moby/client/pkg/versions/compare_test.go

## Purpose
`compare_test.go` tests the Moby client behavior for compare.

## Important APIs, Types, And Functions
Test functions: `TestCompareVersion`. Referenced routes or paths: none.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/pkg/versions/compare_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_create.go -->
# sources/cloud-native/moby/client/plugin_create.go

## Purpose
`plugin_create.go` implements the Moby client surface for plugin create. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `PluginCreateOptions`, `PluginCreateResult`. Functions: `PluginCreate`. Important fields: `PluginCreateOptions` has `RepoName`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/plugins/create`; uses client helper(s) `postRaw`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `io`, `net/http`, `net/url`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_disable.go -->
# sources/cloud-native/moby/client/plugin_disable.go

## Purpose
`plugin_disable.go` implements the Moby client surface for plugin disable. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `PluginDisableOptions`, `PluginDisableResult`. Functions: `PluginDisable`. Important fields: `PluginDisableOptions` has `Force`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/disable`, `/plugins/`; uses client helper(s) `post`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `net/url`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_disable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_disable_test.go -->
# sources/cloud-native/moby/client/plugin_disable_test.go

## Purpose
`plugin_disable_test.go` tests the Moby client behavior for plugin disable.

## Important APIs, Types, And Functions
Test functions: `TestPluginDisableError`, `TestPluginDisable`. Referenced routes or paths: `/plugins/plugin_name/disable`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_disable_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_enable.go -->
# sources/cloud-native/moby/client/plugin_enable.go

## Purpose
`plugin_enable.go` implements the Moby client surface for plugin enable. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `PluginEnableOptions`, `PluginEnableResult`. Functions: `PluginEnable`. Important fields: `PluginEnableOptions` has `Timeout`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/enable`, `/plugins/`; uses client helper(s) `post`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `net/url`, `strconv`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_enable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_enable_test.go -->
# sources/cloud-native/moby/client/plugin_enable_test.go

## Purpose
`plugin_enable_test.go` tests the Moby client behavior for plugin enable.

## Important APIs, Types, And Functions
Test functions: `TestPluginEnableError`, `TestPluginEnable`. Referenced routes or paths: `/plugins/plugin_name/enable`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_enable_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_inspect.go -->
# sources/cloud-native/moby/client/plugin_inspect.go

## Purpose
`plugin_inspect.go` implements the Moby client surface for plugin inspect. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `PluginInspectOptions`, `PluginInspectResult`. Functions: `PluginInspect`. Important fields: `PluginInspectResult` has `Plugin`, `Raw`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/json`, `/plugins/`; uses client helper(s) `get`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `github.com/moby/moby/api/types/plugin`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
most risk sits in route/query compatibility and correct response body closure.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_inspect_test.go -->
# sources/cloud-native/moby/client/plugin_inspect_test.go

## Purpose
`plugin_inspect_test.go` tests the Moby client behavior for plugin inspect.

## Important APIs, Types, And Functions
Test functions: `TestPluginInspectError`, `TestPluginInspectWithEmptyID`, `TestPluginInspect`. Referenced routes or paths: `/plugins/plugin_name`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_install.go -->
# sources/cloud-native/moby/client/plugin_install.go

## Purpose
`plugin_install.go` implements multi-step plugin installation: privilege lookup, permission acceptance, pull progress streaming, optional argument setting, and optional enablement.

## Important APIs, Types, And Functions
Types: `PluginInstallOptions`, `PluginInstallResult`, `pluginOptions`. Functions: `PluginInstall`, `tryPluginPrivileges`, `tryPluginPull`, `checkPluginPermissions`, `getRegistryAuth`, `setRegistryAuth`, `getPrivilegeFunc`, `getAcceptAllPermissions`, `getAcceptPermissionsFunc`, `getRemoteRef`. Important fields: `PluginInstallOptions` has `Disabled`, `AcceptAllPermissions`, `RegistryAuth`, `RemoteRef`, `PrivilegeFunc`, `AcceptPermissionsFunc`; `PluginInstallResult` has `io.ReadCloser`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/plugins/`, `/plugins/privileges`, `/plugins/pull`; uses client helper(s) `delete`, `get`, `post`. Unauthorized registry responses can trigger a caller-provided privilege callback and one retry with refreshed `X-Registry-Auth`. Image or plugin references are normalized before request construction, preventing malformed names from reaching the daemon.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `errors`, `fmt`, `io`, `net/http`, `net/url`, `github.com/containerd/errdefs`, `github.com/distribution/reference`, `github.com/moby/moby/api/types/plugin`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
malformed or schema-incompatible daemon JSON propagates as decode errors; callers must close returned streams or consume iterator helpers to avoid response leaks; auth retry paths must close failed responses and preserve the refreshed header; install cleanup depends on the goroutine observing `retErr`; streaming failures can affect rollback behavior.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_install.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_list.go -->
# sources/cloud-native/moby/client/plugin_list.go

## Purpose
`plugin_list.go` implements the Moby client surface for plugin list. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `PluginListOptions`, `PluginListResult`. Functions: `PluginList`. Important fields: `PluginListOptions` has `Filters`; `PluginListResult` has `Items`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/plugins`; uses client helper(s) `get`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `net/url`, `github.com/moby/moby/api/types/plugin`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
malformed or schema-incompatible daemon JSON propagates as decode errors; callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_list_test.go -->
# sources/cloud-native/moby/client/plugin_list_test.go

## Purpose
`plugin_list_test.go` tests the Moby client behavior for plugin list.

## Important APIs, Types, And Functions
Test functions: `TestPluginListError`, `TestPluginList`. Referenced routes or paths: `/plugins`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_push.go -->
# sources/cloud-native/moby/client/plugin_push.go

## Purpose
`plugin_push.go` implements the Moby client surface for plugin push. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `PluginPushOptions`, `PluginPushResult`. Functions: `PluginPush`. Important fields: `PluginPushOptions` has `RegistryAuth`; `PluginPushResult` has `io.ReadCloser`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/plugins/`, `/push`; uses client helper(s) `post`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `io`, `net/http`, `github.com/moby/moby/api/types/registry`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_push.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_push_test.go -->
# sources/cloud-native/moby/client/plugin_push_test.go

## Purpose
`plugin_push_test.go` tests the Moby client behavior for plugin push.

## Important APIs, Types, And Functions
Test functions: `TestPluginPushError`, `TestPluginPush`. Referenced routes or paths: `/plugins/plugin_name`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_push_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_remove.go -->
# sources/cloud-native/moby/client/plugin_remove.go

## Purpose
`plugin_remove.go` implements the Moby client surface for plugin remove. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `PluginRemoveOptions`, `PluginRemoveResult`. Functions: `PluginRemove`. Important fields: `PluginRemoveOptions` has `Force`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/plugins/`; uses client helper(s) `delete`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `net/url`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_remove_test.go -->
# sources/cloud-native/moby/client/plugin_remove_test.go

## Purpose
`plugin_remove_test.go` tests the Moby client behavior for plugin remove.

## Important APIs, Types, And Functions
Test functions: `TestPluginRemoveError`, `TestPluginRemove`. Referenced routes or paths: `/plugins/plugin_name`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_set.go -->
# sources/cloud-native/moby/client/plugin_set.go

## Purpose
`plugin_set.go` implements the Moby client surface for plugin set. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `PluginSetOptions`, `PluginSetResult`. Functions: `PluginSet`. Important fields: `PluginSetOptions` has `Args`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/plugins/`, `/set`; uses client helper(s) `post`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_set.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_set_test.go -->
# sources/cloud-native/moby/client/plugin_set_test.go

## Purpose
`plugin_set_test.go` tests the Moby client behavior for plugin set.

## Important APIs, Types, And Functions
Test functions: `TestPluginSetError`, `TestPluginSet`. Referenced routes or paths: `/plugins/plugin_name/set`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_set_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_upgrade.go -->
# sources/cloud-native/moby/client/plugin_upgrade.go

## Purpose
`plugin_upgrade.go` implements plugin upgrade with the same permission/authentication contract used by plugin install.

## Important APIs, Types, And Functions
Types: `PluginUpgradeOptions`, `PluginUpgradeResult`. Functions: `PluginUpgrade`, `tryPluginUpgrade`, `getRegistryAuth`, `setRegistryAuth`, `getPrivilegeFunc`, `getAcceptAllPermissions`, `getAcceptPermissionsFunc`, `getRemoteRef`. Important fields: `PluginUpgradeOptions` has `Disabled`, `AcceptAllPermissions`, `RegistryAuth`, `RemoteRef`, `PrivilegeFunc`, `AcceptPermissionsFunc`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/plugins/`, `/upgrade`; uses client helper(s) `post`. Unauthorized registry responses can trigger a caller-provided privilege callback and one retry with refreshed `X-Registry-Auth`. Image or plugin references are normalized before request construction, preventing malformed names from reaching the daemon.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `fmt`, `io`, `net/http`, `net/url`, `github.com/distribution/reference`, `github.com/moby/moby/api/types/plugin`, `github.com/moby/moby/api/types/registry`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks; auth retry paths must close failed responses and preserve the refreshed header.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/plugin_upgrade.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/releases/v0.1.0-beta.toml -->
# sources/cloud-native/moby/client/releases/v0.1.0-beta.toml

## Purpose
`v0.1.0-beta.toml` is a release metadata file for the client module. It records module versioning/release configuration rather than Go runtime behavior.

## Important APIs, Types, And Functions
No Go APIs are defined. The important keys are the TOML release fields consumed by the repository's release tooling.

## Control Flow
There is no executable control flow. Release automation reads the file declaratively when building or publishing the client module version.

## State And Persistence
The file is persistent repository metadata. It does not affect daemon runtime state but can affect published module/release artifacts.

## Dependencies And Integration Points
It integrates with the Moby client release process and any scripts that scan `client/releases/*.toml`.

## Risks
Incorrect version metadata can produce wrong release notes, tags, or module publishing behavior. Because it is declarative, schema drift in release tooling is the main risk.

## Test Signals
No direct Go tests target this file in the subset. Validation is expected from release tooling or configuration checks outside the client unit-test path.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/releases/v0.1.0-beta.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/request.go -->
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
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/request.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/request_test.go -->
# sources/cloud-native/moby/client/request_test.go

## Purpose
`request_test.go` tests the Moby client behavior for request.

## Important APIs, Types, And Functions
Test functions: `TestSetHostHeader`, `TestPlainTextError`, `TestResponseErrors`, `TestInfiniteError`, `TestCanceledContext`, `TestDeadlineExceededContext`, `TestPrepareJSONRequest`. Referenced routes or paths: `/test`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/request_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/secret_create.go -->
# sources/cloud-native/moby/client/secret_create.go

## Purpose
`secret_create.go` implements the Moby client surface for secret create. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `SecretCreateOptions`, `SecretCreateResult`. Functions: `SecretCreate`. Important fields: `SecretCreateOptions` has `Spec`; `SecretCreateResult` has `ID`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/secrets/create`; uses client helper(s) `post`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `github.com/moby/moby/api/types/swarm`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
malformed or schema-incompatible daemon JSON propagates as decode errors; callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/secret_create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/secret_create_test.go -->
# sources/cloud-native/moby/client/secret_create_test.go

## Purpose
`secret_create_test.go` tests the Moby client behavior for secret create.

## Important APIs, Types, And Functions
Test functions: `TestSecretCreateError`, `TestSecretCreate`. Referenced routes or paths: `/secrets/create`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/secret_create_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/secret_inspect.go -->
# sources/cloud-native/moby/client/secret_inspect.go

## Purpose
`secret_inspect.go` implements the Moby client surface for secret inspect. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `SecretInspectOptions`, `SecretInspectResult`. Functions: `SecretInspect`. Important fields: `SecretInspectResult` has `Secret`, `Raw`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/secrets/`; uses client helper(s) `get`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `github.com/moby/moby/api/types/swarm`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
most risk sits in route/query compatibility and correct response body closure.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/secret_inspect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/secret_inspect_test.go -->
# sources/cloud-native/moby/client/secret_inspect_test.go

## Purpose
`secret_inspect_test.go` tests the Moby client behavior for secret inspect.

## Important APIs, Types, And Functions
Test functions: `TestSecretInspectError`, `TestSecretInspectSecretNotFound`, `TestSecretInspectWithEmptyID`, `TestSecretInspect`. Referenced routes or paths: `/secrets/secret_id`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/secret_inspect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/secret_list.go -->
# sources/cloud-native/moby/client/secret_list.go

## Purpose
`secret_list.go` implements the Moby client surface for secret list. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `SecretListOptions`, `SecretListResult`. Functions: `SecretList`. Important fields: `SecretListOptions` has `Filters`; `SecretListResult` has `Items`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/secrets`; uses client helper(s) `get`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `encoding/json`, `net/url`, `github.com/moby/moby/api/types/swarm`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
malformed or schema-incompatible daemon JSON propagates as decode errors; callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/secret_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/secret_list_test.go -->
# sources/cloud-native/moby/client/secret_list_test.go

## Purpose
`secret_list_test.go` tests the Moby client behavior for secret list.

## Important APIs, Types, And Functions
Test functions: `TestSecretListError`, `TestSecretList`. Referenced routes or paths: `/secrets`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/secret_list_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/secret_remove.go -->
# sources/cloud-native/moby/client/secret_remove.go

## Purpose
`secret_remove.go` implements the Moby client surface for secret remove. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `SecretRemoveOptions`, `SecretRemoveResult`. Functions: `SecretRemove`. Important fields: .

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/secrets/`; uses client helper(s) `delete`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/secret_remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/secret_remove_test.go -->
# sources/cloud-native/moby/client/secret_remove_test.go

## Purpose
`secret_remove_test.go` tests the Moby client behavior for secret remove.

## Important APIs, Types, And Functions
Test functions: `TestSecretRemoveError`, `TestSecretRemove`. Referenced routes or paths: `/secrets/secret_id`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/secret_remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/secret_update.go -->
# sources/cloud-native/moby/client/secret_update.go

## Purpose
`secret_update.go` implements the Moby client surface for secret update. It is a thin, typed wrapper over Docker Engine API request helpers, translating Go options into query parameters, headers, and JSON request or response bodies.

## Important APIs, Types, And Functions
Types: `SecretUpdateOptions`, `SecretUpdateResult`. Functions: `SecretUpdate`. Important fields: `SecretUpdateOptions` has `Version`, `Spec`; `SecretUpdateResult` has `}`, `func`, `id,`, `if`, `return`, `}`.

## Control Flow
The main path constructs `url.Values` and/or an API body, calls the shared request helper, defers `ensureReaderClosed` for finite responses, and decodes daemon JSON into the result type. Streaming calls intentionally return the response body to the caller wrapped in cancel-aware or JSON-message readers. This file targets `/secrets/`, `/update`; uses client helper(s) `post`.

## State And Persistence
The file holds no durable local state. Persistent effects occur on the Docker daemon: images, networks, nodes, plugins, secrets, services, or authentication state are created, updated, deleted, or streamed by the API call. Client-side state is limited to context cancellation, response body ownership, and in `Ping`, negotiated API-version fields on `Client`.

## Dependencies And Integration Points
Dependencies include `context`, `net/url`, `github.com/moby/moby/api/types/swarm`. Integration is through `Client` request helpers in `request.go`, API model packages under `github.com/moby/moby/api/types`, and daemon HTTP routes.

## Risks
callers must close returned streams or consume iterator helpers to avoid response leaks.

## Test Signals
Companion tests in this subset exercise error propagation, route/method construction, empty identifier handling, response decoding, version/auth branches, and success decoding where applicable. Coverage is mostly httptest-style unit coverage around the request helper boundary rather than live daemon integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/secret_update.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/secret_update_test.go -->
# sources/cloud-native/moby/client/secret_update_test.go

## Purpose
`secret_update_test.go` tests the Moby client behavior for secret update.

## Important APIs, Types, And Functions
Test functions: `TestSecretUpdateError`, `TestSecretUpdate`. Referenced routes or paths: `/secrets/secret_id/update`.

## Control Flow
The tests construct a fake client/server or small package example, drive the public API under success and failure conditions, and assert returned errors, status handling, request paths, query strings, JSON bodies, or decoded results. Test helpers usually arrange response status/body and then verify that the client generated the exact daemon API contract.

## State And Persistence
All state is in-memory test state. No daemon or registry persistence occurs; fake handlers capture requests and return fixture JSON or errors.

## Dependencies And Integration Points
The tests integrate the file under test with shared client helpers, Moby API type fixtures, `testing`, `httptest`-style client construction, and errdefs checks where unauthorized/not-found behavior matters.

## Risks
The main risk is drift between asserted routes/query encodings and the Docker Engine API. Error tests also guard against response-body leaks and against losing typed errdef classification.

## Test Signals
These are the direct test signals for the adjacent implementation. They cover normal success, daemon error responses, connection errors, empty IDs, invalid references, auth retry behavior, and option serialization according to the named test cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/secret_update_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/service_create.go -->
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
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/service_create.go -->
