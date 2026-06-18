<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/client/build_prune.go -->
# sources/cloud-native/moby/client/build_prune.go

## Purpose
Implements BuildKit/build-cache pruning through the daemon client.

## Important APIs, Types, And Functions
- Exported types: BuildCachePruneOptions, BuildCachePruneResult.
- Exported functions/methods: BuildCachePrune.
- `BuildCachePruneOptions` fields include All, ReservedSpace, MaxUsedSpace, MinFreeSpace, Filters.
- `BuildCachePruneResult` fields include Report.
- Source comments highlight: BuildCachePruneOptions hold parameters to prune the build cache. BuildCachePruneResult holds the result from the BuildCachePrune method.
- It builds query parameters for boolean and byte-size limits, gates newer options by API version, sends a POST request, and decodes a prune report.

## Control Flow
- The exported client method builds query parameters and/or a request body, invokes the daemon endpoint through the shared client transport, checks the HTTP response, and decodes JSON when the endpoint returns a body.
- Shared transport helpers visible in the file include `post`.

## State And Persistence
- The client method itself is stateless; persistent effects happen on the daemon side through build-cache or checkpoint APIs.
- Prune state is destructive daemon-side cache state; request options bound how much cache can be removed.

## Dependencies And Integration Points
- Imports: `context`, `encoding/json`, `fmt`, `net/url`, `strconv`, `github.com/moby/moby/api/types/build`, `github.com/moby/moby/client/pkg/versions`.
- Integrates with the `Client` request helpers (`get`, `post`, `delete`, `sendRequest`, `checkResponseErr`, or version negotiation as present) and daemon HTTP API endpoints.

## Risks And Edge Cases
- Client risk centers on endpoint path construction, query parameter spelling, API-version gating, and preserving daemon error details.

## Test Signals
- Package-level tests include `checkpoint_create_test.go`, `checkpoint_list_test.go`, `checkpoint_remove_test.go`, `client_example_test.go`, `client_mock_test.go`.
- Client tests typically use mock HTTP responders to assert method, path, query parameters, body encoding, decoding, and error wrapping.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/client/build_prune.go -->
