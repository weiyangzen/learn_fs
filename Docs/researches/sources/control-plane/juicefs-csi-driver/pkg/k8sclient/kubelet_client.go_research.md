## sources/control-plane/juicefs-csi-driver/pkg/k8sclient/kubelet_client.go

### Purpose
`kubelet_client.go` implements a minimal HTTPS client for the kubelet `/pods/` endpoint. `PodMount` uses it to list local running pods faster than the API server and avoid mount-pod reuse/listing races.

### Important APIs, Types, And Functions
Constants define the default timeout and service account token file. `KubeletClient` stores host, port, and `http.Client`. `KubeletClientConfig` mirrors kubelet transport config fields. `makeTransport()` builds TLS/bearer-token transports. `NewKubeletClient(host, port)` reads cert/key/timeout env vars and creates the client. `Access()` validates `/pods/`. `GetNodeRunningPods()` fetches and decodes a `corev1.PodList`. `checkKubeletAccessErr()` tracks repeated access failures and exits after five.

### Control Flow
Construction chooses service-account bearer token unless client cert/key env vars are set, configures insecure TLS with server name `kubelet`, applies `KUBELET_TIMEOUT`, builds transport, and returns an HTTPS client. `Access` and `GetNodeRunningPods` perform GET requests, drain/close bodies, require 2xx status, decode JSON for pod lists, and reset/increment the global error counter.

### State, Persistence, And Dependencies
No Kubernetes objects are mutated. Internal process state includes global `kubeletAccessErrCount`. Dependencies include `net/http`, client-go transport/TLS helpers, service-account token file, kubelet HTTPS endpoint, environment variables, and Kubernetes core types.

### Integration Points
`NewPodMount` creates this client when `config.KubeletPort` and `config.HostIp` are set and `Access()` succeeds. `PodMount.listMountPodsOfUniqueId` uses `GetNodeRunningPods()` before falling back to API server listing.

### Risks
`checkKubeletAccessErr` calls `os.Exit(1)` after repeated failures, which can terminate the CSI node process from a helper path. TLS defaults are insecure unless CA material is provided. The package-global error counter applies across all client instances. `/pods/` requires kubelet authn/authz permissions that vary by cluster.

### Test Signals
No tests are listed. Useful tests would use `httptest.Server` for success/status/decode errors, env parsing for timeout/certs, and access error counter behavior without actually exiting.
