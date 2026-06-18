# sources/control-plane/longhorn/chart/templates/httproute.yaml

Purpose: optionally exposes the Longhorn UI through Gateway API `HTTPRoute` instead of the older Ingress API.

Important APIs/types/functions: Gateway API `gateway.networking.k8s.io/v1` `HTTPRoute`, `.Values.httproute.enabled`, `parentRefs`, `hostnames`, path match `type` and `value`, annotations, labels, and backendRef to `longhorn-frontend` port 80.

Control flow: when enabled, the template renders one `longhorn-httproute`. It copies configured parent references with defaults for group and kind, optionally emits hostnames, then creates a single rule matching the configured path and forwarding to the frontend service.

State and persistence: persistent state is the HTTPRoute object. It does not create Gateways, TLS certs, or Services; those must exist separately. Runtime routing state is controlled by the installed Gateway controller.

Dependencies/integration: depends on Gateway API CRDs and a compatible Gateway controller, a `longhorn-frontend` service from `deployment-ui.yaml`, and user-provided `parentRefs` that point to existing Gateway listeners. It may coexist with, or replace, `ingress.yaml` depending on values.

Risks: rendering `gateway.networking.k8s.io/v1` fails if the cluster lacks the CRD or only supports older Gateway versions. Empty `parentRefs` may leave controller-specific route attachment behavior ambiguous. No TLS or auth is configured here, so exposure security is delegated to the Gateway.

Test signals: `helm template` with disabled/enabled routes, multiple parentRefs, cross-namespace parentRefs, hostnames, Exact and PathPrefix matching. Cluster tests should confirm Accepted/ResolvedRefs conditions and that `longhorn-frontend:80` receives traffic.
