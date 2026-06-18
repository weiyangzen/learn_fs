<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/samples/kustomization.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/samples/kustomization.yaml

## Purpose
Collects sample custom resources for bundle/manifests generation.

## Important APIs, Types, And Functions
Includes `beegfs_v1_beegfsdriver.yaml` and retains kubebuilder scaffold marker.

## Control Flow
Used by `config/manifests/kustomization.yaml` to include sample CRs.

## State And Persistence
No runtime state unless samples are applied to a cluster.

## Dependencies And Integration Points
Depends on the BeegfsDriver sample and CRD.

## Risks And Edge Cases
Adding more samples without updating CSV `alm-examples` may leave OLM UI examples incomplete.

## Test Signals
No direct tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/samples/kustomization.yaml -->
