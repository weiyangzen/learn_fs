<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/bases/beegfs.csi.netapp.com_beegfsdrivers.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/crd/bases/beegfs.csi.netapp.com_beegfsdrivers.yaml

## Purpose
Generated Kubernetes apiextensions.k8s.io/v1 CRD for the namespaced `BeegfsDriver` API in group `beegfs.csi.netapp.com`. It is the operator's public configuration and status contract for deploying the BeeGFS CSI driver.

## Important APIs, Types, And Functions
Defines `spec.containerImageOverrides`, `spec.containerResourceOverrides`, `spec.logLevel`, `spec.nodeAffinityControllerService`, `spec.nodeAffinityNodeService`, and `spec.pluginConfig`. Status exposes Kubernetes-style `conditions`. Required fields are sparse, but nested file-system configs require `sysMgmtdHost` and node configs require `nodeList`.

## Control Flow
The API server validates objects against this schema before the controller reads them. Kustomize later applies `patches/singleton.yaml` to restrict metadata.name to `csi-beegfs-cr`.

## State And Persistence
Persisted state is the `BeegfsDriver` custom resource and its status subresource. Plugin configuration is persisted in the CR and rendered by the controller into a ConfigMap for driver pods.

## Dependencies And Integration Points
Generated from the operator API Go types with controller-gen v0.16.5. Integrated by `config/crd/kustomization.yaml`, OLM CSV descriptors, samples, and envtest setup.

## Risks And Edge Cases
The schema repeats Kubernetes core structures and is large, so drift from Go types can hide until regeneration. `beegfsClientConf` values must be strings, which is easy to violate in hand-written YAML. OpenShift form views may not render map fields reliably.

## Test Signals
Envtest loads this base CRD and validates invalid log levels. The singleton name patch is not loaded by envtest, so that constraint depends on kustomize output rather than controller tests.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/crd/bases/beegfs.csi.netapp.com_beegfsdrivers.yaml -->
