<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/scorecard/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/scorecard/kustomization.yaml

## Purpose
Builds the operator scorecard test configuration.

## Important APIs, Types, And Functions
Includes base config and applies JSON6902 patches for basic and OLM scorecard suites.

## Control Flow
Kustomize appends test entries to the base Configuration before bundle generation.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Depends on `patches/basic.config.yaml` and `patches/olm.config.yaml`.

## Risks And Edge Cases
Patch target must match the base object exactly. Scorecard image version is pinned in patches.

## Test Signals
Enables scorecard coverage for spec checks and OLM bundle validation.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/scorecard/kustomization.yaml -->
