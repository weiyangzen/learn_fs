<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manifests/bases/beegfs-csi-driver-operator.clusterserviceversion.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/manifests/bases/beegfs-csi-driver-operator.clusterserviceversion.yaml

## Purpose
Base OLM ClusterServiceVersion metadata for publishing the BeeGFS CSI driver operator.

## Important APIs, Types, And Functions
Declares owned CRD `beegfsdrivers.beegfs.csi.netapp.com`, spec/status descriptors, provider/maintainer links, minKubeVersion 1.19.0, supported OwnNamespace install mode, and container image `ghcr.io/thinkparq/beegfs-csi-driver-operator:v1.8.0`.

## Control Flow
OLM consumes the rendered CSV from the manifests kustomization to display UI descriptors and manage operator lifecycle.

## State And Persistence
CSV is persisted by OLM and tracks install/upgrade status externally to this file.

## Dependencies And Integration Points
Must stay aligned with CRD schema, sample CRs, manager image, bundle annotations, and scorecard expectations.

## Risks And Edge Cases
`alm-examples` is empty despite samples being included elsewhere. Descriptor paths are manually extensive and can drift from CRD/API fields. `install.spec.deployments` is null in this base and relies on bundle generation overlays.

## Test Signals
Scorecard OLM tests validate bundle structure, CRD validation, resources, descriptors, and status descriptors.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/manifests/bases/beegfs-csi-driver-operator.clusterserviceversion.yaml -->
