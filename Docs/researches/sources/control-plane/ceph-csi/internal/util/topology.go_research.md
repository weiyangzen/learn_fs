<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/topology.go -->
## sources/control-plane/ceph-csi/internal/util/topology.go

Purpose: converts Kubernetes node labels and CSI topology requirements into Ceph-CSI topology maps and topology-constrained pool selections.

APIs: `GetTopologyFromDomainLabels` reads requested node labels from Kubernetes and returns CSI topology segments prefixed with `topology.<driverName>/`. `GetTopologyFromRequest` parses JSON `topologyConstrainedPools` from CreateVolume parameters and returns it with accessibility requirements. `MatchPoolAndTopology` filters to a requested pool before matching. `FindPoolAndTopology` prefers matching `Preferred` topology entries, then `Requisite`. `matchPoolToTopology` and `extractDomainsFromlabels` implement domain-label matching.

Control flow: label input is comma-split and checked for duplicates, then Kubernetes node labels are fetched; missing requested labels error. Pool matching treats a configured pool's domain segments as requirements that must all match the requested topology domain map.

State and persistence: no persistence. Reads current Kubernetes Node labels through `k8s.GetNodeLabels`.

Dependencies: CSI protobuf types, internal k8s and log packages, JSON parsing.

Integration points: used during driver topology publication and volume creation when StorageClass parameters include topology-constrained pools.

Risks: label domain extraction uses the substring after `/`; labels without `/` produce the full string due to index `-1`, which may be intentional but is subtle. `GetTopologyFromDomainLabels` is hard to unit test because it calls Kubernetes directly. Empty domain segments in a configured pool can act as a broad match.

Test signals: `topology_test.go` thoroughly covers pool/topology matching but leaves node-label fetching commented out as a TODO requiring client injection.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/topology.go -->
