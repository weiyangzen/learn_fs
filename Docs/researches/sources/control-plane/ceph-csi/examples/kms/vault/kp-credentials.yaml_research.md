# sources/control-plane/ceph-csi/examples/kms/vault/kp-credentials.yaml

Purpose: example Secret for IBM Key Protect credentials.

Important fields and flow: Secret `ceph-csi-kp-credentials` contains API key, customer root key ID, optional session token, and CRK ARN.

State, dependencies, and integration: referenced by IBM Key Protect KMS configuration entries.

Risks and test signals: sample values must be replaced. Valid credentials and service instance settings are required for encryption key lifecycle tests.
