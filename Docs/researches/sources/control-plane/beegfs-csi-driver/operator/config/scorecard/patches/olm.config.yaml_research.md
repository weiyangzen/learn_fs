<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/scorecard/patches/olm.config.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/scorecard/patches/olm.config.yaml

## Purpose
Adds OLM-focused scorecard validation tests.

## Important APIs, Types, And Functions
Appends tests for bundle validation, CRDs with validation, CRDs with resources, spec descriptors, and status descriptors, all using `quay.io/operator-framework/scorecard-test:v1.19.1`.

## Control Flow
Kustomize appends all entries to the parallel scorecard stage.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Validates consistency among CSV, CRDs, and bundle resources.

## Risks And Edge Cases
Descriptor-heavy CSVs can pass stale semantic descriptions if paths remain syntactically valid.

## Test Signals
Direct scorecard signal for OLM bundle readiness.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/scorecard/patches/olm.config.yaml -->
