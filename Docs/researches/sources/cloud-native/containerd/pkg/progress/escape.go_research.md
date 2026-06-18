<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/escape.go -->
# sources/cloud-native/containerd/pkg/progress/escape.go

## Purpose
Centralizes ANSI escape sequences used by progress rendering.

## Important APIs, Types, And Functions
Defines escape, reset, red, and green constants; red is currently unused and annotated for lint suppression.

## Control Flow
No control flow.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Consumed by Bar formatting and potentially other progress terminal output.

## Risks And Edge Cases
Assumes ANSI-capable output; callers writing to non-terminal sinks will include raw escape bytes.

## Test Signals
No direct tests; effects are visible through formatted progress output.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/progress/escape.go -->
