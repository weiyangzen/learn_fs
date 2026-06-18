# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/topology/topology.go

## Purpose
`topology.go` extracts Kubernetes/Rook node labels into Ceph CRUSH topology data and validates that topology labels across nodes are internally consistent. It supports standard Kubernetes region/zone labels, Rook-specific CRUSH labels, custom hostname labels through `k8sutil.LabelHostname()`, topology affinity strings for portable PVC OSDs, and conflict detection before unsafe CRUSH map layouts are accepted.

## Important APIs, Types, and Functions
Public APIs are `ExtractOSDTopologyFromLabels()`, `GetDefaultTopologyLabels()`, and `CheckTopologyConflicts()`. Internal helpers are `rookTopologyLabelsOrdered()`, `allKubernetesTopologyLabelsOrdered()`, `kubernetesTopologyLabelToCRUSHLabel()`, `extractTopologyFromLabels()`, and `formatTopologyAffinity()`. Package variables define `KubernetesTopologyLabels`, `CRUSHTopologyLabels`, and `CRUSHMapLevelsOrdered`.

## Control Flow, State, and Persistence
Extraction iterates topology labels from highest to lowest CRUSH hierarchy, records non-empty values, and sets topology affinity to the lowest non-host topology label found. It then walks labels from lowest to highest and removes higher-level duplicate values so the lowest level wins, logging duplicate topology values. Public extraction normalizes all values through `client.NormalizeCrushName()`. Conflict checking builds a hierarchy excluding host, collects distinct normalized values per key, rejects explicit empty label values, verifies each child value appears under at most one nearest parent value, and enforces cross-key uniqueness for topology values.

## Dependencies and Integration Points
The topology package depends on Kubernetes node labels, `k8sutil.LabelHostname()` for default or custom hostname label selection, Ceph client CRUSH-name normalization, and Rook OSD code that uses extracted topology in CRUSH locations and portable OSD topology affinity. `GetDefaultTopologyLabels()` feeds discovery/watch label configuration.

## Risks
The hierarchy is order-sensitive: Kubernetes region/zone are treated as top layers, Rook labels are ordered from datacenter down to chassis, and host is excluded from conflict checks. Duplicate values are silently removed from extracted topology except for warning logs, which can change resulting CRUSH location. Conflict detection rejects reuse of the same normalized value under different topology keys, even across different nodes, and rejects child values appearing under multiple parents. Empty labels are fatal only when the key exists with an empty value.

## Test Signals
`topology_test.go` covers ordering, normalization, custom hostname labels, ignored invalid labels, topology affinity selection, default label string generation, parent/child conflicts, cross-key duplicate values, empty label rejection, missing child labels, disjoint subtrees, and valid minimal topologies.
