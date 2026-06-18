<!-- BEGIN_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-v1/kustomization.yaml -->
# sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-v1/kustomization.yaml

## Purpose
Small Kustomize overlay that builds the base deployment but retags the `juicedata/juicefs-csi-driver` image to `csi-v1`.

## Important APIs, Types, and Resources
Uses Kustomize `images` transformer with `name: juicedata/juicefs-csi-driver` and `newTag: csi-v1`; resources come from `../base`.

## Control Flow
Kustomize loads base resources and rewrites matching image references in controller/node workloads to the compatibility tag. No resource shape changes occur.

## State and Persistence
Stateless source file; rendered image tags persist in workload pod templates when applied.

## Dependencies and Integration Points
Depends on exact image name matching and Kustomize image transformer semantics. Integrates with compatibility testing or release workflows for the `csi-v1` driver image.

## Risks
If the base image name changes or includes registry prefixes unexpectedly, retagging may not apply. A moving `csi-v1` tag also weakens reproducibility.

## Test Signals
Run `kustomize build`, confirm image tags, and smoke-test CSI registration and volume operations with the retagged image.
<!-- END_FILE_RESEARCH: sources/control-plane/juicefs-csi-driver/deploy/kubernetes/csi-v1/kustomization.yaml -->
