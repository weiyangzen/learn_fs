<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/cainjection_in_beegfsdrivers.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/cainjection_in_beegfsdrivers.yaml

## Purpose
Optional cert-manager CA injection patch for the BeegfsDriver CRD.

## Important APIs, Types, And Functions
Adds `cert-manager.io/inject-ca-from: $(CERTIFICATE_NAMESPACE)/$(CERTIFICATE_NAME)` to the CRD metadata.

## Control Flow
Only participates when uncommented in the CRD kustomization and cert-manager variables are enabled in the parent overlay.

## State And Persistence
No local state. When applied, cert-manager mutates the persisted CRD with a CA bundle for webhook clients.

## Dependencies And Integration Points
Depends on cert-manager, kustomize vars, and conversion webhook configuration.

## Risks And Edge Cases
Incorrect variable wiring leaves an unresolved annotation or points CA injection at the wrong Certificate. OLM comments note cert-manager is not supported in that bundle path.

## Test Signals
No direct tests; render-time validation is needed if webhook support is enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/patches/cainjection_in_beegfsdrivers.yaml -->
