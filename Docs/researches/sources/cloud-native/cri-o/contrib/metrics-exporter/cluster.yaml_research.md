# sources/cloud-native/cri-o/contrib/metrics-exporter/cluster.yaml

## Purpose
Kubernetes manifest deploying cri-o-metrics-exporter with namespace, service account, RBAC, deployment, and service.

## Important APIs, Types, and Functions
Defines Namespace, ServiceAccount, ClusterRole for listing nodes, ClusterRoleBinding, namespace Role for ConfigMap get/create/update, RoleBinding, Deployment with CRIO_METRICS_PORT and POD_NAMESPACE env, and Service on port 80 to targetPort 8080.

## Control Flow
Apply creates the namespace/RBAC first, starts one exporter pod, lets main.go list nodes and update a ConfigMap, then exposes the exporter through a ClusterIP Service.

## State and Persistence
Persists Prometheus scrape configuration into a ConfigMap named after namespace/service; Deployment has no volumes and relies on env/in-cluster service account token.

## Dependencies
Depends on Kubernetes RBAC APIs, apps/v1 Deployment, exporter image quay.io/crio/metrics-exporter:latest, node list permission, and ConfigMap write permission.

## Integration Points
Tied to main.go default namespace/service/configMap names and Prometheus consuming the generated ConfigMap/service target.

## Risks and Edge Cases
RBAC permits cluster-wide node listing; imagePullPolicy Always plus latest risks non-reproducible rollout; no probes or securityContext are defined; node address selection in code assumes usable first node address.

## Test Signals
Manifest validation and pod logs are test signals; exporter should create/update ConfigMap and serve per-node proxy endpoints.
