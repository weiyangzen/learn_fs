<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-ibm-kp-secret.in -->
# sources/control-plane/rook/tests/manifests/test-kms-ibm-kp-secret.in

Purpose: env-substituted Secret template for IBM Key Protect KMS tests. It supplies the API key used by Rook encryption configuration.

Important structure: defines `v1/Secret` named `rook-ibm-kp-token` in namespace `rook-ceph`, with `stringData.IBM_KP_SERVICE_API_KEY` populated from `$IBM_KP_SERVICE_API_KEY`.

State, persistence, and integration: creates a Kubernetes Secret consumed by `tokenSecretName: rook-ibm-kp-token` in the companion IBM Key Protect KMS spec fragment. Dependencies include environment substitution and Rook KMS integration. Risks include accidental plaintext key exposure in generated manifests/logs and missing environment variables producing unusable secrets. Test signals come from cluster encryption startup and key retrieval against IBM Key Protect.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-ibm-kp-secret.in -->
