<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/kustomizeconfig.yaml -->
## sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/kustomizeconfig.yaml

### Purpose
`kustomizeconfig.yaml` tells kustomize that vars should be substituted inside StorageClass `parameters`.

### Important APIs, Types, And Functions
It defines one `varReference` with `kind: StorageClass` and `path: parameters`.

### Control Flow
During kustomize build, `$(SECRET_NAME)` and `$(SECRET_NAMESPACE)` occurrences under StorageClass parameters are eligible for substitution.

### State, Persistence, And Dependencies
No standalone state is created. It depends on kustomize config semantics and is consumed by the sibling kustomization.

### Integration Points
This file is necessary for `resources.yaml` StorageClass secret parameters to reference the generated Secret.

### Risks
If kustomize var support changes, the StorageClass can be rendered with unresolved `$(...)` strings. The reference is broad to all StorageClass parameters in this kustomization.

### Test Signals
Build output should show concrete secret name/namespace values in all four CSI secret parameter keys.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/kustomizeconfig.yaml -->
