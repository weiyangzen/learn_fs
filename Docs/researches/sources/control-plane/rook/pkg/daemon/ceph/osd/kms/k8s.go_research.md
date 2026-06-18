# sources/control-plane/rook/pkg/daemon/ceph/osd/kms/k8s.go

This file implements Kubernetes Secrets as a KMS backend for OSD encryption keys.

`storeSecretInKubernetes()` generates an OSD encryption Secret and creates it in the cluster namespace, tolerating already-exists errors. `updateSecretInKubernetes()` fetches the Secret, updates `StringData` with the dmcrypt key, and writes it back. `getKubernetesSecret()` fetches the Secret and returns the `dmcrypt-key` data value. `generateOSDEncryptedKeySecret()` sets the generated name, namespace, `pvc_name` label, `StringData`, Rook Secret type, and owner reference through `clusterInfo.OwnerInfo`. `GenerateOSDEncryptionSecretName()` prefixes PVC names with `rook-ceph-osd-encryption-key`. `IsK8s()` accepts providers `kubernetes` and `k8s`.

State is Kubernetes Secret objects in the Ceph cluster namespace. Dependencies include the Kubernetes clientset, Rook owner-reference handling, `k8sutil.RookType`, and Ceph cluster info. Integration points are the generic KMS `Config` implementation and OSD encryption/key-rotation flows.

Risks include ignoring already-existing create conflicts without verifying content, returning an empty string when the expected key is absent, and relying on owner-reference setup. `k8s_test.go` covers only deterministic secret-name generation; CRUD behavior is not directly tested in this work item.
