<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/configmap.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/configmap.go

**Purpose:** Provides a thin helper to retrieve a Kubernetes ConfigMap by namespace/name.

**Important APIs and functions:** `GetConfigMap` obtains a client with `NewK8sClient`, calls `CoreV1().ConfigMaps(namespace).Get(context.TODO(), name, metav1.GetOptions{})`, and wraps connection or get errors with resource identity.

**Control flow, state, and persistence:** Read-only API call with no local cache. Uses `context.TODO`, so callers cannot cancel the request through this helper.

**Dependencies and integration points:** Depends on Kubernetes corev1 types, metav1, and the shared k8s client helper. It integrates with any code needing dynamic config from Kubernetes.

**Risks and test signals:** Lack of caller context can hang until client-go timeouts. There are no tests or fake-client coverage in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/configmap.go -->
