# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/k8s_test.go

This minimal test file verifies the naming convention for Kubernetes-backed OSD encryption key Secrets.

`TestGenerateOSDEncryptionSecretName` asserts that PVC name `set1-data-0-7dwll` becomes `rook-ceph-osd-encryption-key-set1-data-0-7dwll`. This protects the stable lookup contract used by `storeSecretInKubernetes()`, `updateSecretInKubernetes()`, and `getKubernetesSecret()`.

State is pure string transformation. Dependencies are only the local KMS package and `testify/assert`. The test does not cover Kubernetes Secret creation, update, fetch, owner references, labels, Secret type, already-exists handling, missing-key behavior, or provider aliases accepted by `IsK8s()`.

The main integration risk is that many callers depend on this exact generated name for idempotent storage and rotation. The test gives a small but important regression signal for that contract while leaving API-server interactions to broader KMS tests elsewhere.
