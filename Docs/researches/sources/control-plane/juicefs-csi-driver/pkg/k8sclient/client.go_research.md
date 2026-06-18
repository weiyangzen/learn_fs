## sources/control-plane/juicefs-csi-driver/pkg/k8sclient/client.go

### Purpose
`client.go` wraps Kubernetes client-go for the CSI driver. It centralizes in-cluster configuration, QPS/Burst tuning, pod/secret/job/PV/PVC/storage/app object CRUD, pod logs, pod exec, events, configmaps, and a small node cache.

### Important APIs, Types, And Functions
Patch payload helper structs model JSON patch values. `K8sClient` stores the Kubernetes interface, rest config, API server list-cache flag, and one-minute node cache. Constructors are `NewClient`, `NewClientWithConfig`, and `newClient`. Resource methods include pod create/get/list/patch/update/delete/log, node list/get/cache, secret CRUD/patch, job CRUD/delete, PV/PVC/storage/app getters, `ExecuteInContainer`, configmap get/create/update, event create/list, and `ListPersistentVolumesByVolumeHandle`.

### Control Flow
`NewClient` reads in-cluster config, applies a 10s timeout, reads `KUBE_QPS` and `KUBE_BURST`, then constructs the wrapper. Listing methods translate label and field selectors into Kubernetes list options; pod listing can set `ResourceVersion=0` when `ENABLE_APISERVER_LIST_CACHE=true`. `CreatePod` sanitizes NUL characters out of toleration keys before submitting. `ExecuteInContainer` builds a pod exec request and streams over SPDY.

### State, Persistence, And Dependencies
Persistent external state is Kubernetes API objects. Internal state includes the rest config and node cache protected by a mutex. Dependencies include client-go Kubernetes, REST, SPDY remotecommand, Kubernetes API types, gRPC status codes, environment variables, and util helpers.

### Integration Points
`PodMount`, `resource` helpers, builder canary jobs, namespace inference, and other CSI components depend on this wrapper. It is also the unit-test seam for fake clients.

### Risks
`ExecuteInContainer` calls `rest.InClusterConfig()` again rather than reusing `K8sClient.RestConfig`, which can diverge in tests or custom configs. `ListPersistentVolumesByVolumeHandle` lists all PVs and filters client-side. Event creation uses the legacy core Event API. `CreatePod` silently mutates toleration keys. Cache and list-cache flags can trade freshness for speed.

### Test Signals
`client_test.go` covers constructor error cases and basic fake-client pod create/get/patch/update/delete. Additional coverage should include selector translation, node cache expiry, secret/job operations, exec config reuse, and toleration key cleanup.
