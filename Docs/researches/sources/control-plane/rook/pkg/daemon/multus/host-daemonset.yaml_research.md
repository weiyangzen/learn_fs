# sources/control-plane/rook/pkg/daemon/multus/host-daemonset.yaml

Purpose: template for host-network checker DaemonSets that validate whether Kubernetes hosts can reach the web server's Multus public-network address.

Important APIs/types/functions: embedded as `hostCheckerDaemonSet` and rendered by `generateHostCheckerDaemonSet()` from `hostCheckerTemplateConfig`. Uses `.NodeType`, `.Placement`, `.NginxImage`, and `.PublicNetworkAddress`.

Control flow: `startHostCheckers()` creates one DaemonSet per node type after the web server is running and a public network address has been discovered. Each pod uses `hostNetwork: true` and a readiness probe that curls the server public address on port 8080. The state machine waits for all host checker pods to become Running, then Ready.

State and persistence behavior: rendered DaemonSets are owned by the validation owner ConfigMap and deleted before client tests unless host-check-only mode exits after this phase.

Dependencies and integration points: depends on host-network permission policy, node placement constraints, Nginx image with `curl`, and the public NAD being routable from host networking. Selected by `hostCheckerAppLabel()`.

Risks: host-network pods may be blocked by Pod Security admission or service account permissions. Failures can indicate host routing/firewall problems rather than Multus attachment problems. The readiness probe assumes `curl` availability.

Test signals: no direct template assertions. Runtime logic includes suggestions for host checker failures in `validation.go`.
