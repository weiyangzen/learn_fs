<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/humaans.go -->
# sources/cloud-native/containerd/pkg/progress/humaans.go

## Purpose
Provides human-readable byte and byte-per-second formatting for progress displays.

## Important APIs, Types, And Functions
Bytes.String formats base-1024 units with docker/go-units. BytesPerSecond represents a byte rate; NewBytesPerSecond computes bytes divided by duration seconds, and String appends /s.

## Control Flow
Callers wrap raw byte counts or call NewBytesPerSecond after measuring duration; String performs the actual rendering.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Depends on docker/go-units and time. Integrates with progress status output and logging.

## Risks And Edge Cases
NewBytesPerSecond does not guard zero duration, so callers must avoid duration=0 to prevent Inf conversion semantics.

## Test Signals
No local tests; behavior is straightforward unit formatting.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/humaans.go -->
