<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/build_cancel.go -->
# sources/cloud-native/moby/client/build_cancel.go

## Purpose
Implements client-side build cancellation by POSTing to the build cancel endpoint with the target
build ID.

## Important APIs, Types, And Functions
- Exported types: BuildCancelOptions, BuildCancelResult.
- Exported functions/methods: BuildCancel.
- Source comments highlight: BuildCancelOptions holds options for [Client.BuildCancel]. BuildCancelResult holds the result of [Client.BuildCancel].
- The method encodes the ID in query parameters and returns an empty result after validating the daemon response.

## Control Flow
- The exported client method builds query parameters and/or a request body, invokes the daemon endpoint through the shared client transport, checks the HTTP response, and decodes JSON when the endpoint returns a body.
- Shared transport helpers visible in the file include `post`.

## State And Persistence
- The client method itself is stateless; persistent effects happen on the daemon side through build-cache or checkpoint APIs.

## Dependencies And Integration Points
- Imports: `context`, `net/url`.
- Integrates with the `Client` request helpers (`get`, `post`, `delete`, `sendRequest`, `checkResponseErr`, or version negotiation as present) and daemon HTTP API endpoints.

## Risks And Edge Cases
- Client risk centers on endpoint path construction, query parameter spelling, API-version gating, and preserving daemon error details.

## Test Signals
- Package-level tests include `checkpoint_create_test.go`, `checkpoint_list_test.go`, `checkpoint_remove_test.go`, `client_example_test.go`, `client_mock_test.go`.
- Client tests typically use mock HTTP responders to assert method, path, query parameters, body encoding, decoding, and error wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/build_cancel.go -->
