<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/snapshotters/annotations_test.go -->
# sources/cloud-native/containerd/pkg/snapshotters/annotations_test.go

## Purpose
Unit tests for snapshotter image-layers annotation truncation.

## Important APIs, Types, And Functions
TestImageLayersLabel builds sample descriptors and a validator with a max key+value length.

## Control Flow
The test calls getLayers for two and five layer cases and checks how many comma-separated digests fit before validation fails.

## State And Persistence
Pure in-memory test state.

## Dependencies And Integration Points
Exercises annotations.go getLayers and validation cutoff behavior.

## Risks And Edge Cases
Counting strings.Split on an empty result would be misleading, but test inputs always include layers and expect non-empty output.

## Test Signals
Direct coverage for avoiding oversized labels.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/snapshotters/annotations_test.go -->
