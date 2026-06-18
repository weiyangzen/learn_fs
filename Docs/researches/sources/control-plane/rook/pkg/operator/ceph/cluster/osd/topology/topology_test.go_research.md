# sources/control-plane/rook/pkg/operator/ceph/cluster/osd/topology/topology_test.go

## Purpose
`topology_test.go` validates CRUSH topology label ordering, extraction, normalization, default label lists, custom hostname labels, and the conflict detector for many valid and invalid node-label hierarchies. It is the main safety net for topology semantics used by OSD placement and CRUSH location generation.

## Important APIs, Types, and Functions
Tests cover `CRUSHMapLevelsOrdered`, `ExtractOSDTopologyFromLabels()`, internal `extractTopologyFromLabels()`, `GetDefaultTopologyLabels()`, and `CheckTopologyConflicts()`. A local `node()` helper constructs `corev1.Node` objects with label maps for table-style subtests.

## Control Flow, State, and Persistence
The extraction tests feed label maps and compare returned topology maps plus affinity strings. They verify that dotted values are normalized by public extraction, duplicate same-value topology labels prefer lower CRUSH levels, invalid unqualified labels are ignored, and custom hostname env changes host label extraction/default label output. Conflict tests construct slices of nodes and assert whether validation errors occur, often checking that error strings include the relevant topology key or reused value.

## Dependencies and Integration Points
The suite depends on Kubernetes stable topology label constants, Rook topology label names, environment variable handling for custom hostnames through `k8sutil`, and Ceph CRUSH-name normalization behavior. Its results protect OSD code that builds CRUSH locations and topology affinity for portable OSD deployments.

## Risks
The extensive conflict matrix shows subtle policy decisions: same rack across zones is invalid, duplicate values across keys are invalid, child labels may be absent on some nodes, a topology can use only one label level, and hostname value overlap is allowed because host is excluded from conflict uniqueness. Tests also encode that missing lower levels do not necessarily imply count-based invalidity; conflicts are about value reuse and parent consistency.

## Test Signals
Signals include ordered CRUSH levels from host through region, cleaned/normalized topology with duplicate-value removal, default topology label strings with and without custom hostname labels, valid single-level topologies, invalid cross-parent child reuse, invalid cross-key value reuse, valid full hierarchy, valid disjoint subtrees, empty value rejection, and real region-zone-hostname layouts.
