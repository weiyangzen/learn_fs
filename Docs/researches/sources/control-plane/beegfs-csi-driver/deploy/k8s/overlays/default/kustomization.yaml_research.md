<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/kustomization.yaml

## Purpose
This is the production-default Kustomize overlay for deploying the BeeGFS CSI driver.

## Important Objects and Fields
It sets namespace `beegfs-csi`, bases on `../../versions/latest`, includes `namespace.yaml`, applies `patches/node-affinity.yaml`, and optionally supports `patches/container-resources.yaml`. It generates `csi-beegfs-config`, `csi-beegfs-connauth`, and `csi-beegfs-tlscerts`. It includes commented image-transform examples for driver and CSI sidecars.

## Control Flow
Rendering applies versioned bases, creates the namespace, applies strategic merge patches, generates hashed ConfigMap/Secret names, and can transform images if users uncomment the section.

## State and Persistence
Applying this overlay creates resources in the `beegfs-csi` namespace and generated config/secret resources with hash suffixes. The namespace object is created by the overlay.

## Dependencies and Integration Points
It depends on version overlays, default config/secret input files, and base manifests. CI direct e2e tests mutate this file by appending image transformations for SHA-tagged test images.

## Risks
The Kustomization uses older `bases` and `patchesStrategicMerge` fields rather than newer `resources`/`patches` style; future Kustomize versions may warn or deprecate them. Users must select compatible version overlays for older Kubernetes clusters. Commented sidecar image examples reference older registry names and may need updates.

## Test Signals
Signals include `kubectl kustomize deploy/k8s/overlays/default`, apply on supported Kubernetes versions, generated hash references, namespace creation, image override behavior, and CI direct e2e deployment.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default/kustomization.yaml -->
