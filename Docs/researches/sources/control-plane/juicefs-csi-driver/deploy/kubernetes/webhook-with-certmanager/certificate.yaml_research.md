<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/certificate.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/certificate.yaml

## Purpose
cert-manager resource bundle for webhook TLS. It defines a self-signed issuer and a certificate whose secret is consumed by webhook-serving controller pods.

## Important APIs, Types, and Resources
Defines `cert-manager.io/v1` `Issuer juicefs-selfsigned` and `Certificate juicefs-cert` in `kube-system`. The certificate lasts 43800h, covers `juicefs-admission-webhook`, `juicefs-admission-webhook.kube-system`, and `juicefs-admission-webhook.kube-system.svc`, and writes `juicefs-webhook-certs`.

## Control Flow
cert-manager reconciles the Issuer and Certificate after apply, creates/renews the target Secret, and later injects the CA into webhook configurations through annotations in companion patches.

## State and Persistence
Persistent state is cert-manager CRDs plus generated TLS Secret. The source file itself has no active state.

## Dependencies and Integration Points
Depends on cert-manager being installed and on webhook Service DNS names matching certificate SANs. Integrates with webhook-with-certmanager overlay and controller TLS volume mounts from base resources.

## Risks
Risks include missing cert-manager CRDs, long-lived self-signed cert rotation expectations, SAN mismatch after service rename, and startup races before the Secret exists.

## Test Signals
Validate by applying to a cert-manager cluster, checking Certificate Ready condition, Secret contents, CA injection, and successful admission HTTPS calls.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/webhook-with-certmanager/certificate.yaml -->
