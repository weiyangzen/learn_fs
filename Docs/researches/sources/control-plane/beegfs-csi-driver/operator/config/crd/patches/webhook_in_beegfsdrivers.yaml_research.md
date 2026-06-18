<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/webhook_in_beegfsdrivers.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/webhook_in_beegfsdrivers.yaml

## Purpose
Optional CRD conversion webhook patch.

## Important APIs, Types, And Functions
Sets `spec.conversion.strategy: Webhook`, references service `webhook-service` in namespace `system`, path `/convert`, and conversionReviewVersions `v1`.

## Control Flow
Inactive until uncommented in kustomization. If enabled, API server conversion requests route through the configured service.

## State And Persistence
No local state. It modifies the persisted CRD conversion configuration.

## Dependencies And Integration Points
Depends on webhook service/deployment overlays and kustomize name/namespace rewriting.

## Risks And Edge Cases
There is only one served/storage version in the current CRD, so webhook support is scaffolded but unused. Enabling without service/certs breaks CRD conversion requests.

## Test Signals
No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/webhook_in_beegfsdrivers.yaml -->
