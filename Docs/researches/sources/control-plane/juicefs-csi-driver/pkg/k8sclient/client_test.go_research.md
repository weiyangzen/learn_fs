## sources/control-plane/juicefs-csi-driver/pkg/k8sclient/client_test.go

### Purpose
`client_test.go` tests a narrow subset of the Kubernetes client wrapper, mainly constructor failure paths and pod CRUD/patch behavior against a fake clientset.

### Important APIs, Types, And Functions
Tests include `TestNewClient`, `TestK8sClient_CreatePod`, `TestK8sClient_GetPod`, `TestK8sClient_PatchPod`, `TestK8sClient_UpdatePod`, and `TestK8sClient_DeletePod`. They use gomonkey to patch `rest.InClusterConfig` and `kubernetes.NewForConfig`, and Kubernetes fake clients for pod operations.

### Control Flow
Constructor tests force nil config, config errors, and new-client errors. CRUD tests create fake `K8sClient` wrappers, optionally seed pods, invoke methods, and compare resulting pod objects or error expectations. Patch tests marshal JSON patch payloads and use `types.JSONPatchType`.

### State, Persistence, And Dependencies
All state is in fake Kubernetes clientsets. Dependencies include GoConvey, gomonkey, client-go fake, Kubernetes API types, and reflection.

### Integration Points
The tests protect the wrapper behavior used by `PodMount` and resource helpers for basic pod lifecycle operations.

### Risks
Coverage is shallow compared with `client.go`: no node cache, list selectors, secrets, jobs, events, logs, exec, configmaps, PV/PVC, or environment QPS/Burst parsing are tested. Fake client behavior differs from real API server validation.

### Test Signals
Failures indicate basic wrapper regressions or changed fake-client object semantics. New wrapper methods should add fake-client or integration tests where possible.
