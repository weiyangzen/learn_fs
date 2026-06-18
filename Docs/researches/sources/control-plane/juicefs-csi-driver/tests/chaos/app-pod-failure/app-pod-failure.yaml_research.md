<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/chaos/app-pod-failure/app-pod-failure.yaml -->
## sources/control-plane/juicefs-csi-driver/tests/chaos/app-pod-failure/app-pod-failure.yaml

### Purpose
This manifest defines a Chaos Mesh `PodChaos` experiment that periodically injects pod failure into one labeled application pod using JuiceFS CSI.

### Important APIs, Types, And Functions
The resource is `pingcap.com/v1alpha1`, kind `PodChaos`, named `app-pod-failure`. Key fields are `action: pod-failure`, `mode: one`, `duration: "60s"`, selector namespace `chaos-victim`, label selector `chaos: victim`, and scheduler cron `@every 5m`.

### Control Flow
Chaos Mesh schedules the experiment every five minutes, selects one matching pod in `chaos-victim`, and applies a pod-failure action for sixty seconds.

### State, Persistence, And Dependencies
Persistent state is the Chaos Mesh custom resource. It depends on Chaos Mesh CRDs/controllers and pods labeled by the overlay. The experiment affects live workload availability.

### Integration Points
The companion kustomization overlays the static-provisioning RWX example with namespace and common labels so this experiment targets the sample app.

### Risks
The selector is broad for all pods in `chaos-victim` with `chaos=victim`; common labels may also apply to non-app resources depending on kustomize output. `pod-failure` can mask storage-specific failures if app recovery behavior is not measured separately.

### Test Signals
Signals include Chaos Mesh admission accepting the CR, one victim pod being failed per schedule, JuiceFS mount recovery after app pod restart/failure, and no unintended namespace targeting.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/chaos/app-pod-failure/app-pod-failure.yaml -->
