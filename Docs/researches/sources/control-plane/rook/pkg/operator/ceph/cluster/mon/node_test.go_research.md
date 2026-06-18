# sources/control-plane/rook/pkg/operator/ceph/cluster/mon/node_test.go

## Purpose
This test file validates node-related monitor behavior: monitor pod placement/host-network behavior, resource memory startup tolerance, and address extraction from Kubernetes nodes.

## Important APIs, Types, And Functions
Tests exercise `makeMonPod()`, `Start()`, and `getNodeInfoFromNode()`. `TestNodeAffinity` constructs mon placement affinity and labels fake nodes to reflect schedulability inputs. `TestHostNetworkSameNode` verifies that a host-networked cluster cannot place three monitors on the same node even when multiple-per-node is otherwise enabled. `TestPodMemory` runs monitor startup across several resource request/limit combinations. `TestHostNetwork` verifies DNS policy, `HostNetwork`, `--public-addr`, and absence of `--public-bind-addr` when a monitor uses host networking. `extractArgValue()` is a local helper for flag assertions.

## Control Flow And State
The tests use fake Kubernetes nodes and fake Rook cluster contexts. They mutate node labels/status and cluster specs, then inspect generated pods or cluster startup errors. They do not persist durable state beyond fake API objects. The host network test captures an important state distinction: a monitor's `UseHostNetwork` setting is preserved independently of the current cluster-level network spec.

## Dependencies And Integration Points
Dependencies include fake Kubernetes clients from Rook test helpers, Ceph client test cluster info, Rook placement/resource APIs, and monitor helpers from `mon_test.go`. The tests integrate monitor pod generation with cluster spec fields such as network, resources, and placement.

## Risks And Test Signals
The tests signal that monitor scheduling is sensitive to host networking, node label availability, and pod resource env vars. They cover the address precedence implemented in `node.go`. `TestNodeAffinity` sets up affinity-related state but contains no final assertion in the visible file, so it is more of a fixture/regression scaffold than a complete behavioral check.
