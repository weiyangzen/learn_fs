# sources/control-plane/ceph-csi/examples/kms/vault/aws-credentials.yaml

Purpose: example Secret for AWS KMS metadata-provider credentials.

Important fields and flow: Secret `ceph-csi-aws-credentials` contains access key, secret key, optional session token, and CMK ARN as `stringData`.

State, dependencies, and integration: consumed by KMS configs referencing AWS metadata providers for encrypted volumes.

Risks and test signals: values are sample credentials and must be replaced. Secret presence plus successful passphrase/key operations validate integration.
