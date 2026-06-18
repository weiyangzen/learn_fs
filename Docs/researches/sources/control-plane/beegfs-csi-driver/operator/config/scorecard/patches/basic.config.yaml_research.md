<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/scorecard/patches/basic.config.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/scorecard/patches/basic.config.yaml

## Purpose
Adds the basic scorecard spec test.

## Important APIs, Types, And Functions
JSON6902 add operation appends `scorecard-test basic-check-spec` using image `quay.io/operator-framework/scorecard-test:v1.19.1`.

## Control Flow
Applied by scorecard kustomization; scorecard later runs the configured entrypoint.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Depends on the Operator Framework scorecard test image.

## Risks And Edge Cases
Pinned image can age relative to operator-sdk versions.

## Test Signals
Provides basic spec validation signal for the bundle.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/scorecard/patches/basic.config.yaml -->
