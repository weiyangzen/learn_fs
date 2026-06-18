<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator.clusterserviceversion.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator.clusterserviceversion.yaml

Purpose: OLM ClusterServiceVersion for installing and describing BeeGFS CSI driver operator v1.8.0.

Important APIs and flow: declares alm example `BeegfsDriver` named `csi-beegfs-cr`, owned CRD descriptors, long-form user documentation, install strategy, RBAC, deployment, install modes, links, maintainers, minimum Kubernetes version, and image `ghcr.io/thinkparq/beegfs-csi-driver-operator:v1.8.0`. The manager runs `/manager --leader-elect --metrics-bind-address=0.0.0.0:8443`, receives `BEEGFS_CSI_DRIVER_NAMESPACE` from its namespace, and exposes health/readiness probes on 8081.

State and persistence: OLM persists the CSV and creates operator Deployment, ServiceAccount, permissions, and watches the owned CRD. The operator then creates driver resources such as ConfigMaps, Secrets, StatefulSets, DaemonSets, PVs, and CSI objects.

Dependencies and integration points: depends on OLM, own-namespace install mode, privileged SCC use, Kubernetes storage APIs, and CRD schema alignment.

Risks and test signals: RBAC is broad because the operator manages CSI storage resources; OpenShift RHCOS caveats are documented. Test with operator-sdk bundle validation, scorecard, CSV phase `Succeeded`, and a sample `BeegfsDriver`.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator.clusterserviceversion.yaml -->
