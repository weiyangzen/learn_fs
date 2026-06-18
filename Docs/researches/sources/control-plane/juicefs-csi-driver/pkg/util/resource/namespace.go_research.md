## sources/control-plane/juicefs-csi-driver/pkg/util/resource/namespace.go

### Purpose
`namespace.go` infers an application namespace when incoming pod data does not include one. It handles direct namespace/request namespace, default fallback, and a JuiceFS PV/PVC-based lookup for controller-owned pods affected by missing namespace data.

### Important APIs, Types, And Functions
`GetNamespace(ctx, client, pod, reqNs)` is the main API. `checkOwner(ctx, client, ownerRefs, namespace)` verifies whether pod owners exist in a candidate namespace for ReplicaSet, StatefulSet, DaemonSet, or Job.

### Control Flow
`GetNamespace` returns `pod.Namespace` if set, then `reqNs` if provided, then `"default"` when the pod has no owners. Otherwise it lists all PVs, filters JuiceFS CSI PVs with claim refs, walks pod PVC volumes, matches PVC names to PV claim names, validates the pod owner in the PV claim namespace, and returns that namespace. NotFound owner checks cause the candidate to be skipped; other errors abort.

### State, Persistence, And Dependencies
The function reads Kubernetes PV and owner resources but does not mutate them. Dependencies include `K8sClient`, Kubernetes core/meta errors, `config.DriverName`, and owner resource getters.

### Integration Points
Used by CSI code that receives incomplete pod namespace context and needs to find the correct PVC namespace for JuiceFS volumes.

### Risks
It lists all PVs and filters client-side, which can be expensive. Matching only by PVC name before owner validation can be ambiguous across namespaces. `checkOwner` returns on the first owner reference, so pods with multiple owners may not be fully considered. Unsupported owner kinds lead to `no owner found`.

### Test Signals
No tests in this subset. Useful tests should cover direct namespace, request namespace, default fallback, owner kind resolution, NotFound skip behavior, and ambiguous PVC names.
