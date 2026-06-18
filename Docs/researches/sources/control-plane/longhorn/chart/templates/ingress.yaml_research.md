# sources/control-plane/longhorn/chart/templates/ingress.yaml

Purpose: optionally exposes the Longhorn UI through Kubernetes `networking.k8s.io/v1` Ingress.

Important APIs/types/functions: Kubernetes `Ingress`, `.Values.ingress.enabled`, `ingressClassName`, primary host, `extraHosts`, TLS hosts and `tlsSecret`, path/pathType, annotation rendering, and backend service `longhorn-frontend` port 80.

Control flow: when enabled, the template emits a single Ingress. It conditionally adds the legacy `ingress.kubernetes.io/secure-backends` annotation, copies user annotations, sets an ingress class if supplied, emits one rule for the main host plus one rule per extra host, and optionally emits one TLS block covering the same host list.

State and persistence: persistent state is the Ingress object and any referenced TLS secret. It does not create the frontend service or ingress controller. Ingress controller runtime state decides actual load-balancer, certificates, and routing behavior.

Dependencies/integration: depends on `longhorn-frontend` from `deployment-ui.yaml`, optional TLS secrets from `tls-secrets.yaml` or external cert managers, and the selected ingress controller. Network policies for UI ingress are tied to `.Values.ingress.enabled` and `.Values.networkPolicies.type`.

Risks: default host `sslip.io` is a placeholder and may not be meaningful without a concrete IP/host strategy. `secureBackends` uses an old annotation key that may not affect modern controllers. Enabling ingress without TLS or auth can expose the Longhorn UI broadly. Extra host and TLS lists must stay aligned with certificates.

Test signals: render default disabled state, single host, extra hosts, TLS enabled, custom annotations, and custom ingressClassName. Validate with controller-specific dry runs and ensure the UI network policy admits the chosen ingress controller pods.
