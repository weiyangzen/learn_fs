<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/kustomization.yaml

## Purpose
This Kustomize overlay is a development-oriented deployment profile for BeeGFS CSI, targeting the `default` namespace and local/test image names.

## Important Objects and Fields
It bases on `../../versions/latest`, applies `patches/image-pull-policy.yaml` and `patches/node-affinity.yaml`, generates `csi-beegfs-config`, `csi-beegfs-connauth`, and `csi-beegfs-tlscerts`, and rewrites images. The driver image is rewritten to `beegfs-csi-driver:latest`; sidecar image rewrite entries point to an internal NetApp registry for older `k8s.gcr.io` names.

## Control Flow
Kustomize applies base resources, then strategic merge patches, generators, namespace transformation, and image transformations. Generated ConfigMap/Secret names are hashed and referenced by workloads.

## State and Persistence
Applying this overlay creates resources in the `default` namespace. Config and secret content comes from sibling YAML files. Image references are transformed for development pulls.

## Dependencies and Integration Points
It depends on version overlays under `deploy/k8s/versions/latest`, patch files, generator input files, and locally available images or registries. It is intended for developer workflows rather than release deployment.

## Risks
The sidecar image names use `k8s.gcr.io`, while current bases use `registry.k8s.io`; those transformations may no longer match sidecar images. `imagePullPolicy: Always` can slow local testing if images are not in a reachable registry. No Namespace resource is included, so `namespace: default` assumes it exists.

## Test Signals
Signals include `kubectl kustomize` output, image transform verification, generated config/secret name references, and local dev cluster deployment smoke tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/deploy/k8s/overlays/default-dev/kustomization.yaml -->
