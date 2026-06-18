# sources/control-plane/ceph-csi/examples/kms/vault/user-secret.yaml

Purpose: user-provided metadata KMS Secret containing an encryption passphrase.

Important fields and flow: Secret `storage-encryption-secret` includes `encryptionPassphrase: test-encryption`.

State, dependencies, and integration: used by metadata KMS modes that reference a user secret by name and optional namespace.

Risks and test signals: static passphrases are sensitive and should be rotated/secured outside examples. Successful encrypted PVC creation validates secret lookup and passphrase use.
