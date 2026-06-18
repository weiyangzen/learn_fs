# sources/control-plane/rook/pkg/operator/k8sutil/node.go

## Purpose
`node.go` contains Rook's Kubernetes node eligibility, hostname, taint/toleration, affinity, and node-list matching helpers. It is central to deciding where Ceph storage daemons can run.

## Important APIs, Types, and Functions
`ValidNode()` and `GetValidNodes()` combine schedulability, placement, and readiness checks. Hostname helpers include `NodeWithHostnameExists()`, `GetNodeNameFromHostname()`, `GetNodeHostName()`, `GetNodeHostNameLabel()`, and `GetNodeHostNames()`. Placement helpers include `NodeMeetsPlacementTerms()`, `NodeMeetsAffinityTerms()`, `NodeIsTolerable()`, and `NodeIsReady()`. Matching helpers include `GetKubernetesNodesMatchingRookNodes()`, `GetNotReadyKubernetesNodes()`, and `RookNodesMatchingKubernetesNodes()`. `GenerateNodeAffinity()` accepts JSON, YAML, or legacy semicolon/comma label syntax.

## Control Flow, State, and Persistence
The file performs read-only Kubernetes API calls via `clientset.CoreV1().Nodes()`. It logs skipped nodes grouped by reason. `scheduleAlways` can override unschedulable and not-ready states. Hostname matching uses `LabelHostname()`, falling back to node names if hostname labels are missing.

## Dependencies and Integration Points
It depends on Rook Ceph CRD placement and storage specs, Kubernetes node/label/selection APIs, fake or real Kubernetes clients, `sigs.k8s.io/yaml`, and `logr` toleration matching. It feeds OSD scheduling, node validation, and CRD-driven affinity generation.

## Risks
`GetNodeHostNames()` reads the hostname label without checking presence, yielding empty values. `GenerateNodeAffinity()` accepts multiple input grammars, which increases ambiguity. Preferred affinity terms are ignored for eligibility, as intended. `scheduleAlways` can allow not-ready nodes, so callers must use it deliberately.

## Test Signals
`node_test.go` covers valid-node filtering, `scheduleAlways`, required affinity, well-known taint ignoring, readiness states, rook/kubernetes node matching, custom hostname labels, JSON/YAML affinity parsing, and not-ready listing.
