<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/health.go -->
# sources/cloud-native/moby/api/types/container/health.go

## Purpose
Defines container health states, summaries, and per-probe log entries, plus validation for health
status strings.

## Important APIs, Types, And Functions
- Exported types: HealthStatus, Health, HealthSummary, HealthcheckResult.
- Exported functions/methods: ValidateHealthStatus.
- Constants: NoHealthcheck, Starting, Healthy, Unhealthy.
- `Health` fields include Status, FailingStreak, Log.
- `HealthSummary` fields include Status, FailingStreak.
- `HealthcheckResult` fields include Start, End, ExitCode, Output.
- Source comments highlight: HealthStatus is a string representation of the container's health. Health stores information about the container's healthcheck results HealthSummary stores a summary of the container's healthcheck results.
- `ValidateHealthStatus` accepts only known status constants and returns a descriptive error for unknown values.

## Control Flow
- Runtime behavior is limited to helper methods such as validators, stringers, comparison functions, sort methods, or error adapters.
- Predicate/validation methods compare string modes or enum values against known constants and return booleans or formatted errors.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `fmt`, `strings`, `time`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Carries timestamp or duration fields that must remain JSON-compatible across daemon/client boundaries.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- Duration and timestamp fields need stable units and timezone/zero-value behavior across API versions.

## Test Signals
- Adjacent test file `sources/cloud-native/moby/api/types/container/health_test.go` exercises related behavior.
- Package-level tests include `config_test.go`, `health_test.go`, `hostconfig_test.go`, `hostconfig_unix_test.go`, `state_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/container/health.go -->
