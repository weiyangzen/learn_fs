# sources/control-plane/ceph-csi/e2e/node.go

Purpose: provides Kubernetes node label and node IP helper functions for topology, read-affinity, and node-targeted e2e behavior.

Important APIs/types/functions: `addLabelsToNodes(f, labels)` applies a label map to all nodes. `deleteNodeLabels(c, labelKeys)` removes labels from all nodes and verifies removal. `checkNodeHasLabel(c, labelKey, labelValue)` asserts every node has a label. `getKubeletIP(c)` returns the first node's `NodeInternalIP`.

Control flow: label helpers list all nodes through client-go, iterate over `nodes.Items`, and use Kubernetes test utils or framework node expectations to add/remove/verify labels. `getKubeletIP()` lists nodes, inspects the first node's status addresses, and returns the internal IP if present.

State and persistence: mutates labels on cluster Node objects. Label cleanup must run to avoid affecting later tests. IP lookup is read-only.

Dependencies and integration points: uses Kubernetes CoreV1 Node APIs, `k8s.io/kubernetes/test/utils`, e2e node expectations, and shared framework. Read-affinity/topology tests elsewhere rely on these helpers.

Risks: all nodes receive identical labels, which is adequate for simple tests but not for multi-zone differentiation. `getKubeletIP()` assumes at least one node and returns only the first node's internal IP. Label removal failures can pollute the cluster for later specs.

Test signals: node labels are visible through API expectations, labels are verified removed, and returned internal IP is usable for tests that need kubelet/node addressing.
