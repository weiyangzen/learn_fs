# sources/control-plane/ceph-csi/charts/ceph-csi-rbd/templates/encryptionkms-configmap.yaml

Purpose: renders KMS configuration for encrypted RBD volumes.

Important APIs/types/functions: emits a `v1/ConfigMap` named from `.Values.kmsConfigMapName`; `data.config.json` is `toJson .Values.encryptionKMSConfig`.

Control flow: RBD node and provisioner pods mount the ConfigMap at `/etc/ceph-csi-encryption-kms-config/`; the driver resolves `encryptionKMSID` StorageClass parameters against this JSON.

State and persistence behavior: Kubernetes ConfigMap holds non-secret KMS connection/config metadata. Secrets/tokens are separate, including service account projected tokens when enabled.

Dependencies and integration points: integrates with Vault/KMS providers, StorageClass encryption options, and `oidc-token` projected volumes.

Risks: KMS JSON shape is provider-specific and weakly validated at template time. Storing sensitive values in this ConfigMap would be an operator error.

Test signals: encryption e2e tests and driver startup/provisioning logs expose invalid KMS config.
