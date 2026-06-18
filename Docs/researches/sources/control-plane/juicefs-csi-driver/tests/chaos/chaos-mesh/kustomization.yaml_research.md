<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/chaos/chaos-mesh/kustomization.yaml -->
## sources/control-plane/juicefs-csi-driver/tests/chaos/chaos-mesh/kustomization.yaml

### Purpose
This kustomization installs or references Chaos Mesh resources required by the JuiceFS chaos tests.

### Important APIs, Types, And Functions
It uses kustomize v1beta1, includes remote resource `github.com/kustless/chaos-mesh`, and sets namespace `chaos-mesh`.

### Control Flow
Kustomize fetches the remote base and renders it into the `chaos-mesh` namespace.

### State, Persistence, And Dependencies
Persistent cluster state is the Chaos Mesh installation. It depends on network access to the remote GitHub base and that base remaining compatible.

### Integration Points
The parent chaos kustomization includes this alongside the app-pod-failure experiment so test clusters can install both Chaos Mesh and the scenario.

### Risks
The remote base is unpinned, so output can change over time or break builds. Network dependency can make validation flaky. Namespace assumptions must match the remote base.

### Test Signals
`kustomize build` and server-side dry-run should verify remote availability, CRD/controller installation, and namespace placement.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/tests/chaos/chaos-mesh/kustomization.yaml -->
