# sources/control-plane/longhorn/chart/templates/network-policies/ui-frontend-network-policy.yaml

Purpose: optionally restricts ingress to Longhorn UI pods when both network policies and chart-managed Ingress are enabled.

Important APIs/types/functions: Kubernetes `NetworkPolicy`, `.Values.networkPolicies.enabled`, `.Values.ingress.enabled`, `.Values.networkPolicies.type`, UI `podSelector`, distribution-specific source selectors for `rke1`, `rke2`, and `k3s`, and TCP ports 8000/80 for the k3s/Traefik path.

Control flow: the template renders only when policies are enabled, ingress is enabled, and `type` is non-empty. It selects UI pods and then chooses exactly one source selector block based on the distribution type. The k3s branch also emits port constraints for 8000 and 80.

State and persistence: persistent state is the NetworkPolicy. It controls which ingress-controller pods can reach Longhorn UI pods behind the frontend service.

Dependencies/integration: depends on ingress controller namespace labels and pod labels matching Rancher/Kubernetes distribution conventions. It is coupled to `ingress.yaml`, not `httproute.yaml`, and to the UI labels in `deployment-ui.yaml`.

Risks: unsupported or mistyped distribution values render a policy with an ingress item but no `from` content, which can produce invalid or overly broad/empty behavior depending on YAML output and API validation. Only k3s adds port restrictions; rke1/rke2 allow all UI pod ports from matching controllers. Custom ingress controllers are not supported by this template.

Test signals: render for `k3s`, `rke2`, `rke1`, empty, and invalid types. In-cluster, verify the selected ingress controller reaches the UI while unrelated pods cannot, and add custom-policy coverage for non-default ingress controllers.
