# sources/control-plane/longhorn/chart/templates/deployment-ui.yaml

Purpose: deploys the Longhorn UI frontend and its service, with optional OpenShift Route/service/oauth-proxy support. It exposes the UI through `longhorn-frontend` and points UI traffic at the internal manager API service.

Important APIs/types/functions: Kubernetes `Deployment`, `Service`, optional OpenShift `Route`, optional OpenShift service with serving cert annotation, `longhorn-ui` container, optional `oauth-proxy` sidecar, env vars `LONGHORN_MANAGER_IP` and `LONGHORN_UI_PORT`, service type handling including `Rancher-Proxy`, LoadBalancer fields, image pull secrets, affinity, priority class, tolerations, and node selectors.

Control flow: when OpenShift and route settings are enabled, the template first emits a reencrypt Route and TLS-serving service. It always emits the UI Deployment, conditionally adds the oauth-proxy sidecar and TLS secret volume for OpenShift route mode, mounts emptyDir locations for nginx writable paths, and then creates the `longhorn-frontend` service on port 80 targeting the container's named `http` port.

State and persistence: desired state lives in Deployment, Service, optional Route, and generated OpenShift serving-cert secret references. Runtime state is ephemeral nginx cache/config/run data in `emptyDir`; UI state is not persisted here. The service can become externally reachable if NodePort or LoadBalancer is selected.

Dependencies/integration: depends on Longhorn UI image values, `longhorn-ui-service-account`, `longhorn-backend:9500`, OpenShift OAuth proxy image values when enabled, ingress/HTTPRoute templates that target `longhorn-frontend`, and network policies that may restrict UI ingress. Rancher-Proxy service labeling integrates with Rancher cluster-service discovery.

Risks: OpenShift route mode renders `image: ""` if no oauth-proxy repository is configured, which is invalid at runtime. The oauth proxy uses a literal cookie secret placeholder and a SAR requiring delete on Longhorn settings, so production OpenShift deployments need careful auth validation. LoadBalancer fields are referenced even though some are not documented near the visible defaults. NodePort null rendering must be accepted by the target API server.

Test signals: render ClusterIP, Rancher-Proxy, NodePort, LoadBalancer, and OpenShift route combinations. Verify `longhorn-frontend` selects UI pods, nginx writable mounts work with restricted filesystems, oauth-proxy starts with a real image and cert secret, and ingress/HTTPRoute/network-policy combinations allow expected UI traffic only.
