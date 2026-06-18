<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/secret.go -->
## sources/control-plane/juicefs-csi-driver/pkg/util/resource/secret.go

### Purpose
`secret.go` centralizes create-or-update behavior for JuiceFS CSI Kubernetes Secrets and provides the generated secret-name convention for unique mount IDs.

### Important APIs, Types, And Functions
`CreateOrUpdateSecret(ctx, client, secret)` creates the Secret when missing or JSON-patches `/data` and `/metadata/ownerReferences` when data or owner refs differ. `GetSecretNameByUniqueId(uniqueId)` returns `juicefs-<uniqueId>-secret`.

### Control Flow
The create/update function runs under `retry.RetryOnConflict`. It gets the old secret from `jfsConfig.Namespace` rather than `secret.Namespace`; a not-found result creates the provided secret. For existing secrets, it compares desired `StringData` against existing `Data`, checks data count differences, merges a single new owner reference by UID when provided, builds replacement JSON Patch operations, and applies them through `PatchSecret`.

### State, Persistence, And Dependencies
The function persists Kubernetes Secret data and owner references. It depends on client-go retry behavior, Kubernetes API error classification, JSON Patch, the project k8s client wrapper, global CSI namespace config, and contextual logging through `util.GenLog`.

### Integration Points
The helper is used by resource/controller code that needs idempotent mount or provisioning secrets. Owner-reference merging lets multiple PVCs or generated objects keep ownership ties without dropping existing references.

### Risks
The get path always uses `jfsConfig.Namespace`, while patch/create logs and the secret object may carry another namespace; callers must understand this namespace convention. Only the first desired owner reference is merged. The patch replaces the entire data map and ownerReferences array, which can remove fields not represented in `StringData` or previously merged owner refs if the comparison path changes. Secret labels, annotations, type, and binary-only `Data` keys are not preserved from the desired object.

### Test Signals
Important tests would cover create on not-found, no-op unchanged secret, StringData value changes, data key count changes, owner-reference merge by UID, conflict retry, namespace mismatch behavior, and preservation/removal semantics for fields outside `/data` and `/metadata/ownerReferences`.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/pkg/util/resource/secret.go -->
