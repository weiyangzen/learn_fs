<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manifests/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/manifests/kustomization.yaml

## Purpose
Top-level kustomization for generating OLM bundle manifests.

## Important APIs, Types, And Functions
Includes the CSV base, default install overlay, samples, and scorecard configuration. Contains commented JSON6902 webhook cleanup for OLM-managed certificates.

## Control Flow
Operator SDK uses this path to assemble bundle manifests. Optional webhook cleanup patches would remove cert volume references because OLM mounts certs itself.

## State And Persistence
No runtime state. Rendered output becomes bundle contents and ultimately OLM-managed cluster resources.

## Dependencies And Integration Points
Integrates config/default, samples, scorecard, and CSV base.

## Risks And Edge Cases
Webhook patch comments reference container and volume indices that can become stale. Optional cert-manager paths should remain disabled for OLM.

## Test Signals
Scorecard and bundle validation consume rendered manifests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manifests/kustomization.yaml -->
