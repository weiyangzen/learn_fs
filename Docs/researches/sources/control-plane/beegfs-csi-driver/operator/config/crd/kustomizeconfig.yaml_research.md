<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/kustomizeconfig.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/crd/kustomizeconfig.yaml

## Purpose
Teaches kustomize how to rewrite CRD conversion webhook service references and annotation variables.

## Important APIs, Types, And Functions
Configures `nameReference` for `spec/conversion/webhook/clientConfig/service/name`, namespace substitution for the matching namespace path, and `varReference` for metadata annotations.

## Control Flow
When webhook/cert-manager patches are enabled, kustomize uses these field specs after resources and patches are loaded.

## State And Persistence
No runtime state. It affects rendered YAML only.

## Dependencies And Integration Points
Integrated by `config/crd/kustomization.yaml`; coordinates with `webhook_in_beegfsdrivers.yaml` and `cainjection_in_beegfsdrivers.yaml`.

## Risks And Edge Cases
Field paths are inert while webhooks are disabled but must remain accurate for future conversion webhook support. Incorrect paths would render manifests that refer to the wrong service or namespace.

## Test Signals
No direct test in this subset; validation would require rendering with webhook patches enabled.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/kustomizeconfig.yaml -->
