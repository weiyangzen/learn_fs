<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/default/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/default/kustomization.yaml

## Purpose
Primary install overlay for deploying the operator into namespace `beegfs-csi`.

## Important APIs, Types, And Functions
Applies `namePrefix: beegfs-csi-driver-operator-`, includes CRD/RBAC/manager bases and metrics service, and carries commented hooks for webhook, cert-manager, Prometheus, and manager component config.

## Control Flow
Kustomize composes all operator resources, prefixes names, rewrites namespaces, and can inject variables if optional features are enabled.

## State And Persistence
No runtime state. Rendered resources create the operator namespace, deployment, service account, RBAC, metrics service, and CRD in the cluster.

## Dependencies And Integration Points
Used by bundle generation through `config/manifests/kustomization.yaml` and manual deployment workflows.

## Risks And Edge Cases
`bases` is an older kustomize field. Optional sections have dependencies across multiple files, so partial uncommenting can produce broken webhook or monitor installs.

## Test Signals
No direct tests; generated manifest validation and operator-sdk bundle checks cover this indirectly.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/default/kustomization.yaml -->
