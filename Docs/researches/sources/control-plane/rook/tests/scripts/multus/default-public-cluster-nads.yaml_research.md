<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/default-public-cluster-nads.yaml -->
# sources/control-plane/rook/tests/scripts/multus/default-public-cluster-nads.yaml

Purpose: NetworkAttachmentDefinition fixtures in the `default` namespace for Multus validation CLI tests.

Important structure: defines `public-net` as macvlan bridge on `eth0` with whereabouts IPv4 range `192.168.20.0/24` and route to `192.168.29.0/24`; defines `cluster-net` as macvlan bridge on `eth0` with whereabouts IPv6 range `fc00::/96`. The comment notes the mixed IPv4/IPv6 setup is unsuitable for CephCluster use but useful for validation tooling.

State, persistence, and integration: creates NAD CRs consumed by test pods launched by `rook multus validation`. Dependencies include Multus, whereabouts, and the `k8s.cni.cncf.io` API. Risks include hard-coded interface/ranges and intentionally invalid-for-Ceph cluster network. Test signals are validation CLI behavior against public/cluster network references.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/default-public-cluster-nads.yaml -->
