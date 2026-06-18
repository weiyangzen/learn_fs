<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/image-pull-policy.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/image-pull-policy.yaml

## Purpose
This development patch forces the BeeGFS driver container images to be pulled every time, supporting repeated use of mutable tags such as `latest`.

## Important Objects and Fields
It patches `StatefulSet/csi-beegfs-controller` and `DaemonSet/csi-beegfs-node`, setting `imagePullPolicy: Always` on the `beegfs` container in both workloads.

## Control Flow
The default-dev Kustomization references this patch, so it is applied automatically for development deployments. Kubernetes will pull the driver image for each pod start rather than relying on a cached image.

## State and Persistence
Applying the overlay persists changed pod templates in the cluster. Changing pull policy can trigger rollout when the rendered pod template changes.

## Dependencies and Integration Points
It depends on stable workload and container names. It supports local/CI development workflows that push repeated `latest` or SHA-like tags to a registry.

## Risks
Clusters without registry access or with locally loaded images may fail to start pods because `Always` bypasses convenient cache behavior. It only affects the driver container, not sidecars.

## Test Signals
Signals include rendered YAML inspection, pod event logs showing image pulls, and developer cluster rollout behavior after rebuilding images.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/patches/image-pull-policy.yaml -->
