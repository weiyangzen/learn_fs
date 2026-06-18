<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/image-pull-policy.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/image-pull-policy.yaml

Purpose: optional patch that forces the BeeGFS driver image to be pulled on every controller and node Pod start.

Important APIs and flow: strategic merge patch targets the `beegfs` container in the `csi-beegfs-controller` StatefulSet and the `csi-beegfs-node` DaemonSet, setting `imagePullPolicy: Always`.

State and persistence: persists in Pod templates and affects future image resolution behavior; existing Pods require rollout to pick up the change.

Dependencies and integration points: relies on Kustomize overlay inclusion, Kubernetes image pull semantics, and the base manifest's container names.

Risks and test signals: useful for mutable tags or development images but increases registry dependency and startup latency. Test by rendering the overlay and checking new Pods include `Always`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/examples/patches/image-pull-policy.yaml -->
