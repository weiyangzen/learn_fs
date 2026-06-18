<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/state_test.go -->
# sources/cloud-native/moby/api/types/container/state_test.go

## Purpose
Exercises Docker container API model behavior through TestValidateContainerState.

## Important APIs, Types, And Functions
- Exported functions/methods: TestValidateContainerState.

## Control Flow
- Control flow is test-driven: each `Test...` function constructs representative values, invokes the API/helper under test, and asserts marshaling, validation, sorting, or HTTP behavior.
- Test cases are table-oriented where the source defines multiple inputs, keeping success and failure paths adjacent.

## State And Persistence
- Tests create in-memory values or mock HTTP responders; no repository state is persisted.

## Dependencies And Integration Points
- Imports: `testing`, `gotest.tools/v3/assert`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Runs under Go test and validates API compatibility with assertions from `gotest.tools` where imported.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- Test value changes can accidentally narrow compatibility coverage if they stop asserting legacy JSON, error, or sort behavior.

## Test Signals
- Direct test functions: TestValidateContainerState.
- Passing `go test` for the package is the acceptance signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/state_test.go -->
