<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/handler.go -->
## sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/handler.go

### Purpose
`handler.go` implements admission webhook handlers for JuiceFS CSI pod sidecar injection, secret validation, static PV uniqueness validation, and mount-pod eviction protection.

### Important APIs, Types, And Functions
`SidecarHandler`, `NewSidecarHandler`, and `Handle` process pod mutation requests. `SecretHandler` validates Secrets through `validator.SecretValidator`. `PVHandler` rejects duplicate static JuiceFS PV volume handles. `EvictPodHandler` denies eviction of referenced mount pods in the CSI namespace. Handler constructors create controller-runtime admission decoders.

### Control Flow
`SidecarHandler.Handle` decodes the pod, skips if injection is already done or disabled by labels, calls `resource.GetVolumes`, allows non-JuiceFS pods, constructs a JuiceFS provider and `SidecarMutate`, mutates the pod, marshals it, and returns a JSON patch response. `SecretHandler` decodes a Secret and calls validator logic. `PVHandler` ignores non-JuiceFS or dynamically provisioned PVs, lists existing PVs by volume handle, and denies if any exist. `EvictPodHandler` only acts on `CREATE` of `pods/eviction` in `config.Namespace`; it fetches the pod, verifies mount-pod labels, then denies eviction when any annotation key equals `util.GetReferenceKey(annotationValue)`.

### State, Persistence, And Dependencies
The handlers read and write no state directly except returning admission patches/decisions. They depend on controller-runtime admission APIs, Kubernetes corev1, project k8s client, JuiceFS provider creation, resource helpers, mutator and validator packages, global config, and common labels.

### Integration Points
Registered webhook paths from `register.go` and installation manifests route Kubernetes admission requests here. Sidecar mutation ties pod admission to PV/PVC lookup, per-PVC secret creation, and mount sidecar generation. PV validation protects static PV uniqueness. Eviction validation integrates with Kubernetes drain/eviction flows.

### Risks
Sidecar injection returns bad request on volume lookup or mutation failures, so webhook `failurePolicy` determines cluster impact. `PVHandler` can deny the new PV because `ListPersistentVolumesByVolumeHandle` includes the current object if API timing changes. `EvictPodHandler` trusts annotation key/value hash convention and only applies in the configured namespace. Secret validation creates a provider with nil clients, so validator behavior depends on provider methods not requiring Kubernetes.

### Test Signals
Important tests include decode failures, skip labels, non-JuiceFS pod allowance, multi-PVC mutation patch shape, mutation errors, secret validation errors, static PV duplicate volume-handle denial, dynamic PV allowance, eviction subresource filtering, not-found pod allowance, non-mount pod allowance, and referenced mount-pod eviction denial.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/webhook/handler/handler.go -->
