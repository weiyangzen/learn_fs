<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/chaos/kustomization.yaml -->
## sources/control-plane/juicefs-csi-driver/tests/chaos/kustomization.yaml

### Purpose
This top-level kustomization groups the JuiceFS CSI chaos test environment.

### Important APIs, Types, And Functions
It includes the `app-pod-failure` scenario and the `chaos-mesh` installation overlay.

### Control Flow
Kustomize renders both child resource trees in one build.

### State, Persistence, And Dependencies
Applying the output creates Chaos Mesh infrastructure and a victim workload/experiment. Dependencies are the two child kustomizations and their remote/local bases.

### Integration Points
This is the entry point for running the chaos fixture in validation pipelines or local clusters.

### Risks
Combining infrastructure and experiment in one kustomization may start chaos as soon as the controller is installed and ready. Remote Chaos Mesh drift can affect the whole top-level build.

### Test Signals
Signals include successful `kustomize build`, CRDs installed before experiment reconciliation, and victim pods correctly labeled/namespaced.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/chaos/kustomization.yaml -->
