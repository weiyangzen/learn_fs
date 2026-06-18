<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/rook-ceph-public-cluster-nads.yaml -->
# sources/control-plane/rook/tests/scripts/multus/rook-ceph-public-cluster-nads.yaml

Purpose: NetworkAttachmentDefinition fixtures in the `rook-ceph` namespace for Rook Ceph Multus integration.

Important structure: defines `public-net` with whereabouts IPv4 range `192.168.20.0/24` and route to `192.168.29.0/24`; defines `cluster-net` with IPv4 range `192.168.21.0/24`. Both use macvlan bridge mode on `eth0`.

State, persistence, and integration: creates NADs referenced by Rook cluster network settings and connection tests. Dependencies include Multus, whereabouts, macvlan-capable nodes, and matching host route DaemonSet. Risks include hard-coded subnets/interface and namespace coupling. Test signals include Ceph daemon address checks showing OSDs on both public and cluster networks and MDS only on public.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multus/rook-ceph-public-cluster-nads.yaml -->
