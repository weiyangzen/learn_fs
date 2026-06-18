<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/webhookconfiguration.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/webhookconfiguration.yaml

## Purpose
Patch fragment adding cert-manager CA injection metadata to the mutating webhook configuration.

## Important APIs, Types, and Resources
Targets `admissionregistration.k8s.io/v1` `MutatingWebhookConfiguration juicefs-admission-webhook` and adds annotation `cert-manager.io/inject-ca-from: kube-system/juicefs-cert`.

## Control Flow
Kustomize merges the annotation into the mutating webhook. cert-manager injects CA data so kube-apiserver can trust the webhook Service TLS certificate.

## State and Persistence
No local state; persisted cluster state is the annotation and injected CA bundle.

## Dependencies and Integration Points
Depends on cert-manager, the named Certificate, and base webhook object identity. Integrates with pod/serverless mutation paths in the CSI controller.

## Risks
Wrong annotation targets or absent cert-manager can make the mutating webhook reject or time out admissions. CA injection delays can affect initial rollout.

## Test Signals
Check rendered annotation, cert-manager injector events, populated `clientConfig.caBundle`, and admission mutation e2e tests.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/webhookconfiguration.yaml -->
