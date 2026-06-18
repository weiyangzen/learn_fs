<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/pkg/snapshotters/annotations.go -->
# sources/cloud-native/containerd/pkg/snapshotters/annotations.go

## Purpose
Adds image reference, manifest digest, layer digest, and remaining-layer-list annotations to layer descriptors during image handling for remote snapshotters.

## Important APIs, Types, And Functions
Constants TargetRefLabel, TargetManifestDigestLabel, TargetLayerDigestLabel, TargetImageLayersLabel; AppendInfoHandlerWrapper; getLayers.

## Control Flow
The wrapper calls the inner handler, then when the descriptor is a manifest it annotates layer children with ref, own digest, manifest digest, and a comma-separated suffix of layer digests capped by label validation.

## State And Persistence
Annotations are in-memory descriptor metadata propagated to snapshotters as labels; no direct persistence here.

## Dependencies And Integration Points
Depends on core/images media-type helpers, labels.Validate, log, and OCI descriptors. Important for remote/lazy snapshotter pull optimization.

## Risks And Edge Cases
Layer list truncation is validation-driven and silently logged at debug. The label names retain cri prefix for compatibility despite non-CRI use.

## Test Signals
annotations_test.go validates layer-list truncation behavior under a synthetic size limit.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/pkg/snapshotters/annotations.go -->
