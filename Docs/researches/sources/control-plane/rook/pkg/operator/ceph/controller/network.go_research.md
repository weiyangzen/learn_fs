# sources/control-plane/rook/pkg/operator/ceph/controller/network.go

## Purpose
`network.go` applies Ceph public and cluster network CIDR settings, including automatic Multus CIDR discovery through a canary command-reporter Job.

## Important APIs, Types, and Functions
`ApplyCephNetworkSettings()` is the entry point. It only acts for host networking or Multus, merges user-provided `spec.network.addressRanges` with auto-discovered ranges, and calls `setNetworkCIDRs()` for `public_network` and `cluster_network`. `discoverCephAddressRanges()` discovers public and cluster ranges in parallel with a 15-minute deadline. `discoverAddressRanges()` builds a network canary `cmdreporter` Job, attaches the selected Multus network, waits for the network-status annotation, captures both the annotation and `ip --json address show`, and cross-references them. `crossReferenceNetworkStatusAndIpResult()`, `cidrForIp()`, and `findAddrInfoForIp()` reduce pod IP/prefix data to stable network CIDRs.

## Control Flow, State, and Persistence
User-specified address ranges are authoritative and skip discovery for that network. Multus discovery launches Kubernetes Jobs and reads their stdout. Applying CIDRs persists Ceph config options through the mon config store (`global public_network` and `global cluster_network`) using `SetIfChanged()`. Empty CIDR lists are logged but not written.

## Dependencies and Integration Points
The file integrates with CephCluster network selectors/address ranges, Multus network attachment annotations, CNI network-status annotations, `cmdreporter`, OSD placement, command reporter labels/annotations, `k8sutil` network parsers, and `config.GetMonStore()`.

## Risks
The canary path is operationally complex and depends on Multus, downward API timing, `ip --json`, network-status annotation format, service account `rook-ceph-cmd-reporter`, and OSD placement being schedulable. Channels are closed by the parent after reads; goroutines must send before close under the current flow. Auto-discovery can delay reconciliation up to 15 minutes. CIDR order follows reported IP order and can cause config churn if upstream order changes. Host-network mode does not auto-discover ranges, so users must specify address ranges if they want Ceph network settings.

## Test Signals
`network_test.go` is broad: it covers discovery success/failures, IPv4/IPv6 CIDR reduction, interface/IP mismatches, missing outputs, cmdreporter errors, placement propagation, explicit address range precedence, hostnet behavior, and mon-store errors. It does not run a real Multus canary.
