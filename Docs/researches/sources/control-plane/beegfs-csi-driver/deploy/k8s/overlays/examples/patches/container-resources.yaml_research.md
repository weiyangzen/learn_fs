<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/container-resources.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/container-resources.yaml

Purpose: optional Kustomize strategic merge patch that sets CPU and memory requests/limits for BeeGFS CSI controller and node containers.

Important APIs and flow: patches the `csi-beegfs-controller` StatefulSet containers `beegfs` and `csi-provisioner`, and the `csi-beegfs-node` DaemonSet containers `beegfs`, `node-driver-registrar`, and `liveness-probe`. Values mirror documented defaults and are meant to be edited before enabling.

State and persistence: changes persist as Pod template resource fields, causing rollout on apply. No runtime state is stored by this file itself.

Dependencies and integration points: depends on Kustomize patch inclusion and exact workload/container names from the base manifests.

Risks and test signals: YAML indentation is fragile in the DaemonSet portion, and invalid resources can break scheduling or patch application. Test with `kustomize build`, Kubernetes server dry-run, and inspection of rendered Pod specs.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/container-resources.yaml -->
