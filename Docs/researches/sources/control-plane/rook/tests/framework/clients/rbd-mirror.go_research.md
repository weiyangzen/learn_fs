# sources/control-plane/rook/tests/framework/clients/rbd-mirror.go

Purpose: `RBDMirrorOperation` manages `CephRBDMirror` resources for tests that validate RBD mirroring daemon deployment.

Important APIs/types/functions: constructor `CreateRBDMirrorOperation`; `Create` and `Delete`.

Control flow: `Create` applies a rendered `CephRBDMirror` manifest, waits for pods labeled `app=rook-ceph-rbd-mirror`, then asserts the expected daemon count in Running state. `Delete` removes the CR through the typed Rook client and ignores not-found errors.

State and persistence behavior: persistent state includes the CephRBDMirror CR and mirror daemon pods. Backend Ceph mirroring state is controlled indirectly by operator reconciliation.

Dependencies and integration points: uses installer manifests, `K8sHelper` pod wait/check methods, Rook typed clientset, Kubernetes API errors, and testify assertions.

Risks: pod checks use only the common app label, so multiple mirror resources in one namespace could affect counts. Delete does not wait for pod or CR finalizer cleanup. Assertions inside `Create` directly fail the test instead of returning detailed errors.

Test signals: expected mirror daemon pod count/running state, CR deletion, and Ceph mirroring status from CLI/client calls in higher-level tests.
