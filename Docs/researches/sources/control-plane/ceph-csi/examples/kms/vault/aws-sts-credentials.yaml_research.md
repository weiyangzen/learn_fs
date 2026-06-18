# sources/control-plane/ceph-csi/examples/kms/vault/aws-sts-credentials.yaml

Purpose: example Secret for AWS STS-backed KMS access.

Important fields and flow: Secret `ceph-csi-aws-credentials` contains role ARN, CMK ARN, and AWS region for fetching temporary credentials.

State, dependencies, and integration: used by KMS configurations with `aws-sts-metadata` to obtain KMS access dynamically.

Risks and test signals: placeholder ARNs/region must match an AWS account and trust setup. Successful encrypted volume creation validates STS and KMS wiring.
