# sources/control-plane/rook/pkg/operator/ceph/controller/label.go

## Purpose
`label.go` serializes detected Ceph versions into Kubernetes-safe labels and applies them to controller-owned resources.

## Important APIs, Types, and Functions
`CephVersionLabelKey` is `ceph-version`. `GetCephVersionLabel()` formats `version.CephVersion` as `Major.Minor.Extra-Build`. `ExtractCephVersionFromLabel()` converts the label back by prepending `ceph version `. `AddCephVersionLabelToDeployment()`, `AddCephVersionLabelToDaemonSet()`, `AddCephVersionLabelToJob()`, and `AddCephVersionLabelToObjectMeta()` initialize label maps if needed and add the version label.

## Control Flow, State, and Persistence
The functions mutate passed Kubernetes objects in memory; persistence happens only when callers create or update those objects. The file explicitly warns not to label pod templates because label changes could force unnecessary daemon restarts during upgrades.

## Dependencies and Integration Points
This integrates with `pkg/operator/ceph/version`, Kubernetes Deployment/DaemonSet/Job/ObjectMeta types, and upgrade/reporting logic that uses labels to track detected Ceph versions.

## Risks
The label format is part of the implicit contract and comments state not to change it. `ExtractCephVersionFromLabel()` depends on the version parser accepting the synthetic `ceph version` prefix. Applying labels to selectors or pod templates by mistake can cause disruptive rollouts.

## Test Signals
No direct test file is included for this source. Useful tests would cover nil resources, nil label maps, round-trip parse/format, and label format compatibility for multi-digit versions.
