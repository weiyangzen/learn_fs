<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/serviceaccounts.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/serviceaccounts.go

**Purpose:** Provides helpers for ServiceAccount token creation and ServiceAccount retrieval.

**Important APIs and functions:** `CreateServiceAccountToken` calls `CoreV1().ServiceAccounts(namespace).CreateToken` with an empty `TokenRequest`. `GetServiceAccount` fetches a ServiceAccount by namespace/name. Both wrap client creation and API errors.

**Control flow, state, and persistence:** These are direct Kubernetes API calls with `context.TODO`. Token creation persists only as an API-issued token response; no local storage is used.

**Dependencies and integration points:** Depends on Kubernetes authentication/v1 and corev1 APIs, metav1, and the shared k8s client. It integrates with workflows that need short-lived service account tokens.

**Risks and test signals:** Empty `TokenRequest` relies on API defaults for audience/expiration. No caller cancellation is available. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/serviceaccounts.go -->
