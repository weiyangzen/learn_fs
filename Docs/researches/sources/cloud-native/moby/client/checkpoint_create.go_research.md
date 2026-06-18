<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/checkpoint_create.go -->
# sources/cloud-native/moby/client/checkpoint_create.go

## Purpose
Implements the client call for creating a container checkpoint.

## Important APIs, Types, And Functions
- Exported types: CheckpointCreateOptions, CheckpointCreateResult.
- Exported functions/methods: CheckpointCreate.
- `CheckpointCreateOptions` fields include CheckpointID, CheckpointDir, Exit.
- Source comments highlight: CheckpointCreateOptions holds parameters to create a checkpoint from a container. CheckpointCreateResult holds the result from [client.CheckpointCreate].
- It converts client options into the checkpoint request body, POSTs to the container checkpoint endpoint, and wraps daemon errors with context.

## Control Flow
- The exported client method builds query parameters and/or a request body, invokes the daemon endpoint through the shared client transport, checks the HTTP response, and decodes JSON when the endpoint returns a body.
- Shared transport helpers visible in the file include `post`.

## State And Persistence
- The client method itself is stateless; persistent effects happen on the daemon side through build-cache or checkpoint APIs.
- Checkpoint state is identified by container ID plus checkpoint ID and optionally scoped by checkpoint directory.

## Dependencies And Integration Points
- Imports: `context`, `github.com/moby/moby/api/types/checkpoint`.
- Integrates with the `Client` request helpers (`get`, `post`, `delete`, `sendRequest`, `checkResponseErr`, or version negotiation as present) and daemon HTTP API endpoints.

## Risks And Edge Cases
- Client risk centers on endpoint path construction, query parameter spelling, API-version gating, and preserving daemon error details.

## Test Signals
- Adjacent test file `sources/cloud-native/moby/client/checkpoint_create_test.go` exercises related behavior.
- Package-level tests include `checkpoint_create_test.go`, `checkpoint_list_test.go`, `checkpoint_remove_test.go`, `client_example_test.go`, `client_mock_test.go`.
- Client tests typically use mock HTTP responders to assert method, path, query parameters, body encoding, decoding, and error wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/checkpoint_create.go -->
