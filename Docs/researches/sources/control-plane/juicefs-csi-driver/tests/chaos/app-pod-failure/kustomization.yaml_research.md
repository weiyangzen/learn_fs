<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/chaos/app-pod-failure/kustomization.yaml -->
## sources/control-plane/juicefs-csi-driver/tests/chaos/app-pod-failure/kustomization.yaml

### Purpose
This kustomization assembles the app-pod-failure chaos scenario by combining a static RWX JuiceFS example with the PodChaos resource.

### Important APIs, Types, And Functions
It uses kustomize v1beta1, includes `../../../examples/static-provisioning-rwx` and `app-pod-failure.yaml`, sets namespace `chaos-victim`, and applies common label `chaos: victim`.

### Control Flow
Kustomize renders the base example and chaos resource into the `chaos-victim` namespace and labels resources so the PodChaos selector can find victim pods.

### State, Persistence, And Dependencies
Rendered manifests create application/storage resources and a Chaos Mesh experiment. It depends on the referenced example path and Chaos Mesh being installed.

### Integration Points
This overlay is included by the parent `tests/chaos/kustomization.yaml`. It links the target app and selector labels for the chaos experiment.

### Risks
Applying common labels to all resources can cause the chaos selector to match pods beyond the intended app if the base creates multiple pods. The relative base path must remain valid.

### Test Signals
Use `kustomize build` to verify namespace/label propagation, referenced base availability, and resulting PodChaos selector matching intended workload pods.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/chaos/app-pod-failure/kustomization.yaml -->
