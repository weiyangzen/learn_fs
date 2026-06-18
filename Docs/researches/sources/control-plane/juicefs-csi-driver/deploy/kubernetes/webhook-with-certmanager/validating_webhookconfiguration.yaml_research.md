<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/validating_webhookconfiguration.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/validating_webhookconfiguration.yaml

## Purpose
Patch fragment adding cert-manager CA injection metadata to the validating webhook configuration.

## Important APIs, Types, and Resources
Targets `admissionregistration.k8s.io/v1` `ValidatingWebhookConfiguration juicefs-admission-webhook` and adds annotation `cert-manager.io/inject-ca-from: kube-system/juicefs-cert`.

## Control Flow
Kustomize merges the metadata annotation into the base validating webhook object. cert-manager's injector later fills the webhook client CA bundle from the named Certificate.

## State and Persistence
No state in the file. Persisted state is the annotation on the ValidatingWebhookConfiguration and cert-manager-managed CA bundle updates.

## Dependencies and Integration Points
Depends on cert-manager CA injector, exact webhook configuration name, and Certificate namespace/name. Integrates with the webhook-with-certmanager overlay.

## Risks
If cert-manager is absent or the annotation points to the wrong Certificate, admission calls fail TLS validation. Patch drift can leave the validating webhook using stale static CA data.

## Test Signals
Render the overlay, inspect annotations, verify CA bundle injection, and run validating-admission negative/positive tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/validating_webhookconfiguration.yaml -->
