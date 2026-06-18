# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/nvmeof.go

Purpose: provides the host-network helper for the Ceph NVMe-oF gateway CRD.

Important APIs/types/functions: `CephNVMeOFGateway.IsHostNetwork` reads `n.Spec.HostNetwork` and falls back to `ClusterSpec.Network.IsHost()`.

Control flow: the method is a simple precedence check. An explicitly set gateway `HostNetwork` pointer wins, preserving both true and false. When the field is nil, the gateway inherits the cluster network policy.

State and persistence: no mutable state or persistence. The method interprets CRD fields only.

Dependencies/integration: depends on `CephNVMeOFGateway`, `ClusterSpec`, and the network helper implementation in the same API package. The operator can use it to decide whether gateway pods should use Kubernetes host networking.

Risks: nil receiver or nil cluster pointer would panic; callers are expected to pass real API objects. There is no local test file in this subset, so behavior is inferred from the identical NFS/object host-network helper pattern and network tests.

Test signals: no direct tests in this item. Regression coverage should include explicit true, explicit false, and nil inheritance from cluster network provider/legacy host-network settings.
