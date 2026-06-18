<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-ibm-kp-spec.in -->
# sources/control-plane/rook/tests/manifests/test-kms-ibm-kp-spec.in

Purpose: env-substituted KMS configuration fragment for IBM Key Protect tests. It configures Rook's `spec.security.kms` section.

Important structure: sets `KMS_PROVIDER: ibmkeyprotect`, injects `$IBM_KP_SERVICE_INSTANCE_ID`, and points `tokenSecretName` to `rook-ibm-kp-token`.

State, persistence, and integration: when merged into a cluster spec, Rook uses IBM Key Protect for encryption key management. Dependencies include the companion Secret template, IBM service instance credentials, and a consuming manifest-generation path. Risks include fragment-only validity, unset substitutions, and external service availability. Test signals are encrypted OSD provisioning and key lifecycle operations succeeding through the KMS provider.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/manifests/test-kms-ibm-kp-spec.in -->
