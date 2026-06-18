<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/checkpoint_list_test.go -->
# sources/cloud-native/moby/client/checkpoint_list_test.go

## Purpose
Exercises Docker API client implementation behavior through TestCheckpointListError,
TestCheckpointList, TestCheckpointListContainerNotFound.

## Important APIs, Types, And Functions
- Exported functions/methods: TestCheckpointListError, TestCheckpointList, TestCheckpointListContainerNotFound.

## Control Flow
- Control flow is test-driven: each `Test...` function constructs representative values, invokes the API/helper under test, and asserts marshaling, validation, sorting, or HTTP behavior.
- Test cases are table-oriented where the source defines multiple inputs, keeping success and failure paths adjacent.

## State And Persistence
- The client method itself is stateless; persistent effects happen on the daemon side through build-cache or checkpoint APIs.
- Checkpoint state is identified by container ID plus checkpoint ID and optionally scoped by checkpoint directory.

## Dependencies And Integration Points
- Imports: `net/http`, `testing`, `github.com/containerd/errdefs`, `github.com/moby/moby/api/types/checkpoint`, `gotest.tools/v3/assert`, `gotest.tools/v3/assert/cmp`.
- Integrates with the `Client` request helpers (`get`, `post`, `delete`, `sendRequest`, `checkResponseErr`, or version negotiation as present) and daemon HTTP API endpoints.
- Runs under Go test and validates API compatibility with assertions from `gotest.tools` where imported.

## Risks And Edge Cases
- Test value changes can accidentally narrow compatibility coverage if they stop asserting legacy JSON, error, or sort behavior.
- Client risk centers on endpoint path construction, query parameter spelling, API-version gating, and preserving daemon error details.

## Test Signals
- Direct test functions: TestCheckpointListError, TestCheckpointList, TestCheckpointListContainerNotFound.
- Passing `go test` for the package is the acceptance signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/checkpoint_list_test.go -->
