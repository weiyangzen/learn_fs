# sources/control-plane/rook/pkg/operator/k8sutil/network.go

## Purpose
`network.go` provides Multus and IP-address helpers for Rook-managed Kubernetes resources. It applies network attachment annotations, parses Multus network status annotations, parses `ip --json address show`, and classifies endpoint address families.

## Important APIs, Types, and Functions
`ApplyMultus()` computes public and, for `rook-ceph-osd`, cluster network selections from `cephv1.NetworkSpec` and writes `k8s.v1.cni.cncf.io/networks`. `ParseNetworkStatusAnnotation()` unmarshals Multus status JSON. `FindNetworkStatusByInterface()` selects a status by interface name. `LinuxIpAddrResult` and `LinuxIpAddrInfo` model the limited JSON fields Rook consumes. `ParseLinuxIpAddrOutput()` validates non-empty JSON. `GetIpAddressType()` returns Kubernetes discovery IPv4 or IPv6 address type and rejects mixed families.

## Control Flow, State, and Persistence
The functions are stateless and mutate only the provided `ObjectMeta`. `ApplyMultus()` always appends public network first, then cluster network for OSDs, preserving a stable annotation order independent of selector map order.

## Dependencies and Integration Points
It depends on Rook Ceph API network helpers, the network-attachment-definition client API, Kubernetes EndpointSlice address types, and `net/netip`. It integrates with pod/service metadata creation and endpoint generation for Multus environments.

## Risks
Only app label `rook-ceph-osd` receives the cluster network, so new cluster-network consumers require code changes. An absent `app` label is treated as unknown and public-only. `GetIpAddressType()` infers family from the first address and validates the rest; invalid or scoped addresses produce errors.

## Test Signals
`network_test.go` covers short and JSON Multus selector syntax, public/cluster ordering, empty and malformed `ip` JSON, IPv4, IPv6, mixed-family, and empty address lists. It does not cover `ParseNetworkStatusAnnotation()` or `FindNetworkStatusByInterface()`.
