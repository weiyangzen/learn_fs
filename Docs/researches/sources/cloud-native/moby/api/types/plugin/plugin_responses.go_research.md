<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/plugin/plugin_responses.go -->
# sources/cloud-native/moby/api/types/plugin/plugin_responses.go

## Purpose
ListResponse contains the response for the Engine API

## Important APIs, Types, And Functions
- Exported types: ListResponse, Privilege, Privileges.
- Exported functions/methods: Len, Less, Swap.
- `Privilege` fields include Name, Description, Value.
- Source comments highlight: ListResponse contains the response for the Engine API Privilege describes a permission the user has to accept upon installing a plugin. Privileges is a list of Privilege

## Control Flow
- Runtime behavior is limited to helper methods such as validators, stringers, comparison functions, sort methods, or error adapters.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.

## Dependencies And Integration Points
- Imports: `sort`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.

## Test Signals
- Package-level tests include `capability_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/plugin/plugin_responses.go -->
