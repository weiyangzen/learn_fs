<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/node.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/node.go

**Purpose:** Reads Kubernetes node metadata used for topology/read-affinity and detects out-of-service nodes by taint.

**Important APIs and functions:** `GetNodeLabels` fetches a Node and returns its labels. `IsNodeOutOfService` fetches a Node and scans taints for `node.kubernetes.io/out-of-service` with `NoExecute` or `NoSchedule`.

**Control flow, state, and persistence:** Both functions make read-only API calls with `context.TODO`. The out-of-service check returns true on the first matching taint/effect and false otherwise.

**Dependencies and integration points:** Depends on Kubernetes corev1, metav1, and the shared client. It integrates with CRUSH location construction, read affinity, and node fencing/health logic.

**Risks and test signals:** No caller cancellation. Errors wrap node names for diagnostics. No direct tests in this subset; fake-client tests would be useful for taint combinations and missing nodes.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/node.go -->
