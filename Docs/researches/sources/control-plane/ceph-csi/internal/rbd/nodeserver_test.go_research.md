<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/nodeserver_test.go -->
# sources/control-plane/ceph-csi/internal/rbd/nodeserver_test.go

## Purpose
`nodeserver_test.go` provides focused unit tests for low-risk helpers in the RBD node server: staging-path construction, boolean option parsing, read-affinity map option composition, and csi-config/read-affinity integration.

## Important APIs, Types, And Functions
Tests are `TestGetStagingPath`, `TestParseBoolOption`, `TestNodeServer_appendReadAffinityMapOptions`, and `TestReadAffinity_GetReadAffinityMapOptions`. The tests instantiate `csi.NodeStageVolumeRequest`, `csi.NodeUnstageVolumeRequest`, `rbdVolume`, `csicommon.CSIDriver`, and `NodeServer`.

## Control Flow
The tests exercise helper inputs in table-driven form. The read-affinity config test writes a temporary JSON csi-config file, constructs CLI read-affinity options from node labels, creates a minimal `NodeServer`, and verifies `util.GetReadAffinityMapOptions` output for enabled, disabled, empty-label, absent-cluster, and CLI-disabled cases.

## State And Persistence
State is test-local. The only filesystem write is the temporary csi-config JSON under `t.TempDir()`. No Ceph cluster or Kubernetes API is contacted.

## Dependencies And Integration Points
The tests depend on CSI protobuf request types, Ceph-CSI deployment config structs, `csicommon`, `util` read-affinity helpers, and `testify/require`. They validate integration between node labels, CLI read-affinity options, and cluster-level read-affinity settings.

## Risks
Coverage is intentionally narrow and does not exercise the CSI RPCs, mount operations, local stash files, encryption, or cgroup QoS. The read-affinity test mutates a shared temp config path across parallel subtests only for reads after one write; that is safe but relies on no later mutation.

## Test Signals
The file confirms helper idempotence and option-string construction. It does not protect the higher-risk staging, rollback, unstage, expand, or publish paths.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/rbd/nodeserver_test.go -->
