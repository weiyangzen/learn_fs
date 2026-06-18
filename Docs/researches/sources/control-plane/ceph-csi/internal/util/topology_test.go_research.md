<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/topology_test.go -->
## sources/control-plane/ceph-csi/internal/util/topology_test.go

Purpose: verifies topology-constrained pool selection logic, including `FindPoolAndTopology` and `MatchPoolAndTopology`.

Coverage: tests nil inputs, empty pool lists, missing pool names, mismatched domain labels/values, empty/partial accessibility requirements, valid singleton and multiple-pool matches, preferred ordering, data pool return, explicit pool filtering success, and non-existent pool errors.

State and dependencies: pure in-memory CSI `TopologyRequirement` and `TopologyConstrainedPool` fixtures; no Kubernetes API calls.

Integration signals: demonstrates that pools with empty or partial domain segments can match a richer requested topology, and preferred requirements are evaluated before requisite entries.

Risks and gaps: `GetTopologyFromDomainLabels` is commented out because Kubernetes label reads are not injectable. The `checkOutput` condition has a precedence pattern that may not fail on all malformed topology maps as intended.

Test signal quality: good for matching semantics, weak for node label integration.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/topology_test.go -->
