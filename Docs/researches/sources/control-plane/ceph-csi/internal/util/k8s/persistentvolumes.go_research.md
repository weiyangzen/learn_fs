<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/persistentvolumes.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/persistentvolumes.go

**Purpose:** Provides a helper to retrieve a Kubernetes PersistentVolume by name.

**Important APIs and functions:** `GetPersistentVolume` obtains a client and calls `CoreV1().PersistentVolumes().Get(context.TODO(), name, metav1.GetOptions{})`, wrapping errors with the PV name.

**Control flow, state, and persistence:** Read-only API call with no local cache and no caller-provided context.

**Dependencies and integration points:** Depends on Kubernetes corev1, metav1, and the shared client helper. It integrates with code that needs PV specs or annotations from the cluster.

**Risks and test signals:** No direct tests here. Risks are the shared client cache race and inability to cancel/timeout through the helper.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/persistentvolumes.go -->
