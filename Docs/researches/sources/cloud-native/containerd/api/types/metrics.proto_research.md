<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/api/types/metrics.proto -->
# sources/cloud-native/containerd/api/types/metrics.proto

## Purpose
Canonical proto definition for generic metric samples.

## Important APIs and Types
`Metric` contains `timestamp`, string `id`, and `data` as protobuf `Any`.

## Control Flow
Schema only.

## State and Persistence
Represents a point-in-time metric sample or stats payload. Storage, aggregation, and display are external.

## Dependencies and Integration Points
Imports protobuf `Any` and `Timestamp`. Integrated with task metrics APIs and platform-specific stats payloads.

## Risks
The schema does not validate metric type, unit, or subject. Consumers need platform-aware decoding and fallback behavior for unknown payloads.

## Test Signals
Metrics service integration tests, unknown `Any` handling, and platform-specific decoding coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/api/types/metrics.proto -->
