<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/hwaddr_test.go -->
# sources/cloud-native/moby/api/types/network/hwaddr_test.go

## Purpose
Exercises network_test behavior through TestHardwareAddr_UnmarshalText,
TestHardwareAddr_MarshalText, TestHardwareAddr_MarshalJSON, TestHardwareAddr_UnmarshalJSON.

## Important APIs, Types, And Functions
- Exported functions/methods: TestHardwareAddr_UnmarshalText, TestHardwareAddr_MarshalText, TestHardwareAddr_MarshalJSON, TestHardwareAddr_UnmarshalJSON.
- Wire JSON fields include mac.

## Control Flow
- Control flow is test-driven: each `Test...` function constructs representative values, invokes the API/helper under test, and asserts marshaling, validation, sorting, or HTTP behavior.
- Test cases are table-oriented where the source defines multiple inputs, keeping success and failure paths adjacent.

## State And Persistence
- Tests create in-memory values or mock HTTP responders; no repository state is persisted.

## Dependencies And Integration Points
- Imports: `encoding/json`, `testing`, `github.com/moby/moby/api/types/network`, `gotest.tools/v3/assert`, `gotest.tools/v3/assert/cmp`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Runs under Go test and validates API compatibility with assertions from `gotest.tools` where imported.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- Test value changes can accidentally narrow compatibility coverage if they stop asserting legacy JSON, error, or sort behavior.

## Test Signals
- Direct test functions: TestHardwareAddr_UnmarshalText, TestHardwareAddr_MarshalText, TestHardwareAddr_MarshalJSON, TestHardwareAddr_UnmarshalJSON.
- Passing `go test` for the package is the acceptance signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/network/hwaddr_test.go -->
