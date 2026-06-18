<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/client.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/client.go

**Purpose:** Creates and caches a Kubernetes clientset and provides small environment/error helpers.

**Important APIs and functions:** `NewK8sClient` uses `KUBERNETES_CONFIG_PATH` with `clientcmd.BuildConfigFromFlags` or in-cluster config, sets protobuf content type, creates a clientset, and stores it in package variable `kubeclient`. `RunsOnKubernetes` checks `KUBERNETES_SERVICE_HOST`. `IgnoreNotFound` maps Kubernetes not-found errors to nil.

**Control flow, state, and persistence:** The client cache is process-global and unsynchronized. Once initialized, later environment changes do not affect the client. No persistent state is written.

**Dependencies and integration points:** Depends on client-go, Kubernetes API errors, runtime content type, rest config, and environment variables. All other `internal/util/k8s` helpers call `NewK8sClient`.

**Risks and test signals:** Concurrent first calls could race on `kubeclient`. Protobuf content type can interact with API server/client support. No direct tests in this subset cover client creation or cache behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/client.go -->
