<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/samples/beegfs_v1_beegfsdriver.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/config/samples/beegfs_v1_beegfsdriver.yaml

## Purpose
Minimal example BeegfsDriver custom resource for typical OpenShift deployment.

## Important APIs, Types, And Functions
Uses apiVersion `beegfs.csi.netapp.com/v1`, kind `BeegfsDriver`, required singleton name `csi-beegfs-cr`, controller/node affinities excluding `node.openshift.io/os_id=rhcos`, and commented image/log/plugin config sections.

## Control Flow
Users apply or edit this sample to create the singleton CR. The controller then renders driver resources from its spec.

## State And Persistence
The sample becomes the persistent desired state for the operator once applied.

## Dependencies And Integration Points
References the CRD schema and is included by samples kustomization and bundle generation.

## Risks And Edge Cases
Comments contain a CRD filename typo (`beegfsdriver` singular). The sample is OpenShift-biased and requires non-RHCOS nodes with BeeGFS client prerequisites.

## Test Signals
No direct test; envtest helper builds a full CR programmatically.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/config/samples/beegfs_v1_beegfsdriver.yaml -->
