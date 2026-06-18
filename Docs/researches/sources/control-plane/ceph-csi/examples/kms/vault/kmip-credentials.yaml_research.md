# sources/control-plane/ceph-csi/examples/kms/vault/kmip-credentials.yaml

Purpose: example Secret for KMIP KMS integration.

Important fields and flow: Secret `ceph-csi-kmip-credentials` provides `CA_CERT`, `CLIENT_CERT`, `CLIENT_KEY`, and `UNIQUE_IDENTIFIER` as `stringData`.

State, dependencies, and integration: referenced by KMIP provider config in KMS ConfigMaps.

Risks and test signals: empty values are placeholders. TLS material and KMIP endpoint must match. Successful encrypted PVC operations validate KMIP connectivity.
