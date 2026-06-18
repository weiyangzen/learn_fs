<!-- BEGIN_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator-controller-manager-metrics-service_v1_service.yaml -->
# sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator-controller-manager-metrics-service_v1_service.yaml

Purpose: OLM bundle Service exposing the operator controller manager metrics endpoint.

Important APIs and flow: creates a v1 `Service` named `beegfs-csi-driver-operator-controller-manager-metrics-service`, selects Pods with `control-plane: controller-manager`, and forwards TCP port 8443 to targetPort 8443.

State and persistence: persists a cluster Service object; no application state is stored.

Dependencies and integration points: integrates with the CSV deployment that runs manager with `--metrics-bind-address=0.0.0.0:8443`, and with metrics RBAC/auth manifests.

Risks and test signals: selector or port mismatch breaks metrics scraping. Test by checking endpoints and authenticated metrics access after OLM install.
<!-- END_FILE_RESEARCH: sources/control-plane/beegfs-csi-driver/operator/bundle/manifests/beegfs-csi-driver-operator-controller-manager-metrics-service_v1_service.yaml -->
