<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/kustomization.yaml -->
## sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/kustomization.yaml

### Purpose
This kustomization defines the reconciliation validation fixture for a dynamic JuiceFS PVC shared by writer and reader deployments.

### Important APIs, Types, And Functions
It sets namespace `default`, common label `juicefs-csi-driver/validation: reconcile`, configuration `kustomizeconfig.yaml`, resource file `resources.yaml`, a `secretGenerator` named `juicefs` from `Secret-juicefs.env`, and vars `SECRET_NAME` and `SECRET_NAMESPACE` for StorageClass parameters.

### Control Flow
Kustomize generates a Secret, resolves vars into StorageClass parameter fields listed by `kustomizeconfig.yaml`, labels resources, and renders the validation workload.

### State, Persistence, And Dependencies
Applying output creates a secret, StorageClass, PVC, and two Deployments. It depends on a local `Secret-juicefs.env` file and kustomize var behavior.

### Integration Points
The generated StorageClass feeds secret names/namespaces into JuiceFS CSI provisioner and node publish flows. The deployments in `resources.yaml` validate read/write visibility through the shared PVC.

### Risks
Kustomize `vars` are deprecated in newer kustomize releases, so future tooling may require replacements. Missing `Secret-juicefs.env` breaks build. The fixture uses namespace `default`, which can collide in shared clusters.

### Test Signals
Signals include successful kustomize build, StorageClass parameters resolved to generated Secret name and namespace, PVC binding, writer appending data, and reader tailing the same file.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/validation/reconcile/kustomization.yaml -->
