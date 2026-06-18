# sources/control-plane/rook/pkg/daemon/multus/client-daemonset.yaml

Purpose: Go template for Multus validation client DaemonSets. Each rendered DaemonSet simulates one Ceph daemon/client type per selected node and checks connectivity to the validation web server over one or more Multus-attached networks.

Important APIs/types/functions: consumed by `templates.go` via embedded variable `clientDaemonSet` and rendered from `clientTemplateConfig`. Template fields include `.NodeType`, `.ClientType`, `.ClientID`, `.NetworksAnnotationValue`, `.Placement`, `.NginxImage`, and `.NetworkNamesAndAddresses`.

Control flow: `ValidationTest.startClients()` renders one DaemonSet per desired OSD and non-OSD client slot. The pod template annotates `k8s.v1.cni.cncf.io/networks` so Multus attaches public and/or cluster networks. For each requested target address, it creates a container with an exec readiness probe running `curl --insecure <addr>:8080`; readiness is therefore the validation signal used by the state machine.

State and persistence behavior: resources are Kubernetes DaemonSets that persist until owner ConfigMap deletion or explicit cleanup. Labels encode app, node type, client type, and client ID for selection and expected-count calculations.

Dependencies and integration points: depends on Nginx image containing `curl`, Multus network annotations, Kubernetes DaemonSet scheduling, node selectors/tolerations from `PlacementConfig`, and readiness probe behavior. It integrates with `clientAppLabel()` and `numPodsReadyWithLabel()` in Go code.

Risks: if the configured image lacks `curl`, validation fails as a networking symptom. `successThreshold: 12`, `failureThreshold: 1`, and `periodSeconds: 5` intentionally make readiness sensitive; slow or bursty networks may look flaky. Empty placement can schedule broadly, so node type definitions must be accurate. Address formatting for IPv6 is handled before template rendering in Go.

Test signals: no direct YAML test; coverage comes indirectly through template rendering paths and validation workflow logic. No test asserts exact security context, readiness probe settings, or annotation rendering.
