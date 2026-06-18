<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/helpers.go -->
# sources/cloud-native/containerd/pkg/tracing/helpers.go

## Purpose
Converts arbitrary Go values to OpenTelemetry attribute key-values.

## Important APIs, Types, And Functions
keyValue handles nil, bool/int/float/string scalar and slice types, fmt.Stringer, JSON-marshaled fallback, and fmt.Sprintf fallback.

## Control Flow
Type switch maps values to the most specific attribute constructor, converting narrower ints to int/int64 slices as needed.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Used by tracing.Attribute and logrus hook field conversion.

## Risks And Edge Cases
Unsupported numeric types such as uint fall through to JSON/string. JSON fallback can expose structured data as a string rather than semantic attributes.

## Test Signals
Indirectly covered by tracing/log behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/tracing/helpers.go -->
