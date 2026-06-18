<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-cr.yaml -->
# sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-cr.yaml

Purpose: operator-mode test resources for deploying the BeeGFS CSI driver custom resource with connection auth.
Important surface: Secret `csi-beegfs-connauth` stores `csi-beegfs-connauth.yaml`; BeegfsDriver CR `csi-beegfs-cr` sets image override variables, controller node affinity, and plugin config stubs.
Control flow/state: the operator reconciles the CR into CSI controller/node services and reads the Secret for connection auth.
Dependencies/integration: requires the BeeGFS CSI operator CRD, `${CSI_IMAGE_NAME}`, `${CSI_IMAGE_TAG}`, `${BEEGFS_MGMTD}`, and `${BEEGFS_SECRET}` substitutions.
Risks/test signals: CR name is fixed by comment; malformed Secret YAML breaks operator reconciliation; test depends on master node label existing for preferred affinity. Operator-created driver pods are the signal.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/test/env/beegfs-ubuntu/csi-beegfs-cr.yaml -->
