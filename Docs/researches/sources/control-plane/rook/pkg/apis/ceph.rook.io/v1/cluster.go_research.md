# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/cluster.go

Purpose: adds behavior helpers to `ClusterSpec` and `CephCluster`.

Important APIs/types/functions: `ClusterSpec.RequireMsgr2`, `ClusterSpec.NetworkEncryptionEnabled`, `ClusterSpec.IsStretchCluster`, `ClusterSpec.ZonesRequired`, and `CephCluster.GetStatusConditions`.

Control flow: `RequireMsgr2` returns true if network connections explicitly require msgr2 or enable compression/encryption. Stretch/zone helpers inspect monitor stretch cluster and zone settings.

State and persistence: reads fields from the CephCluster spec/status; conditions persist in `status.conditions`.

Dependencies/integration: used by reconcilers and status helpers when deciding network protocol requirements and zone-aware scheduling.

Risks: enabling compression implicitly requires msgr2; callers must understand that behavior.

Test signals: unit tests for nil connections, encryption/compression combinations, stretch cluster zones, and status condition pointer mutation.
