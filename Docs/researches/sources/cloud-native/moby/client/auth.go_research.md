<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/auth.go -->
# sources/cloud-native/moby/client/auth.go

## Purpose
Defines the client-side auth configuration helper type alias.

## Important APIs, Types, And Functions
- It re-exports registry auth configuration through the client package for backward-compatible API use.

## Control Flow
- The exported client method builds query parameters and/or a request body, invokes the daemon endpoint through the shared client transport, checks the HTTP response, and decodes JSON when the endpoint returns a body.

## State And Persistence
- The client method itself is stateless; persistent effects happen on the daemon side through build-cache or checkpoint APIs.

## Dependencies And Integration Points
- Imports: `context`, `github.com/moby/moby/api/types/registry`.
- Integrates with the `Client` request helpers (`get`, `post`, `delete`, `sendRequest`, `checkResponseErr`, or version negotiation as present) and daemon HTTP API endpoints.

## Risks And Edge Cases
- Client risk centers on endpoint path construction, query parameter spelling, API-version gating, and preserving daemon error details.

## Test Signals
- Package-level tests include `checkpoint_create_test.go`, `checkpoint_list_test.go`, `checkpoint_remove_test.go`, `client_example_test.go`, `client_mock_test.go`.
- Client tests typically use mock HTTP responders to assert method, path, query parameters, body encoding, decoding, and error wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/auth.go -->
