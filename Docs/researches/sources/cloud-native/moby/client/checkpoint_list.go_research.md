<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/checkpoint_list.go -->
# sources/cloud-native/moby/client/checkpoint_list.go

## Purpose
Implements the client call for listing checkpoints on a container.

## Important APIs, Types, And Functions
- Exported types: CheckpointListOptions, CheckpointListResult.
- Exported functions/methods: CheckpointList.
- `CheckpointListOptions` fields include CheckpointDir.
- `CheckpointListResult` fields include Items.
- Source comments highlight: CheckpointListOptions holds parameters to list checkpoints for a container. CheckpointListResult holds the result from the CheckpointList method.
- It adds optional checkpoint directory query state, GETs the endpoint, and decodes checkpoint summaries.

## Control Flow
- The exported client method builds query parameters and/or a request body, invokes the daemon endpoint through the shared client transport, checks the HTTP response, and decodes JSON when the endpoint returns a body.
- Shared transport helpers visible in the file include `get`.

## State And Persistence
- The client method itself is stateless; persistent effects happen on the daemon side through build-cache or checkpoint APIs.
- Checkpoint state is identified by container ID plus checkpoint ID and optionally scoped by checkpoint directory.

## Dependencies And Integration Points
- Imports: `context`, `encoding/json`, `net/url`, `github.com/moby/moby/api/types/checkpoint`.
- Integrates with the `Client` request helpers (`get`, `post`, `delete`, `sendRequest`, `checkResponseErr`, or version negotiation as present) and daemon HTTP API endpoints.

## Risks And Edge Cases
- Client risk centers on endpoint path construction, query parameter spelling, API-version gating, and preserving daemon error details.

## Test Signals
- Adjacent test file `sources/cloud-native/moby/client/checkpoint_list_test.go` exercises related behavior.
- Package-level tests include `checkpoint_create_test.go`, `checkpoint_list_test.go`, `checkpoint_remove_test.go`, `client_example_test.go`, `client_mock_test.go`.
- Client tests typically use mock HTTP responders to assert method, path, query parameters, body encoding, decoding, and error wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/checkpoint_list.go -->
