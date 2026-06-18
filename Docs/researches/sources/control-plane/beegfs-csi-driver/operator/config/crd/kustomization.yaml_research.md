<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/crd/kustomization.yaml

## Purpose
Builds the BeegfsDriver CRD package for the default operator overlay.

## Important APIs, Types, And Functions
Includes the generated CRD base, leaves webhook and cert-manager strategic-merge patches commented, applies the JSON6902 singleton patch, and registers `kustomizeconfig.yaml`.

## Control Flow
`config/default` consumes this kustomization. Kustomize loads the base CRD, applies `patches/singleton.yaml` to the CRD schema, and uses the configuration file for future webhook name/namespace substitution.

## State And Persistence
No runtime state. The rendered CRD becomes persistent cluster API state when applied.

## Dependencies And Integration Points
Depends on the CRD base and patch files. It is part of the bundle/manifests generation path through `config/manifests/kustomization.yaml`.

## Risks And Edge Cases
Webhook and CA patches are intentionally disabled; enabling them requires coordinated edits here and in default overlays. The singleton patch uses JSON paths into `spec.versions[0]`, so version ordering matters.

## Test Signals
No direct test. Integration coverage is indirect through generated manifests and envtest loading the unpatched base.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/kustomization.yaml -->
