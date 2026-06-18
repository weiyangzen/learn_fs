# sources/cloud-native/cri-o/internal/hostport/hostport_manager_test.go

## Purpose
Defines shared IPv4 and IPv6 hostport test fixtures used by iptables, nftables, and meta hostport manager tests.

## Important APIs, Types, And Functions
- `testCase` groups sandbox ID, pod name, pod IP, and mappings.
- `testCasesV4` covers TCP, UDP, SCTP, specific HostIP, duplicate host port on different HostIPs, and duplicate host port across protocols.
- `testCasesV6` mirrors core IPv6 scenarios including `::1` HostIP.

## Control Flow
No executable test specs are defined. Other tests iterate over these fixtures to add/remove hostports and compare backend-specific expected state.

## State And Persistence
No mutable state. The fixed IDs intentionally produce stable hash outputs used in expected iptables chain names and nftables comments.

## Dependencies And Integration Points
Uses Kubernetes `v1.Protocol` and the local `PortMapping` type. Tightly coupled to expected rule/element arrays in backend tests.

## Risks And Edge Cases
Changing fixture IDs, ports, HostIPs, or ordering invalidates many expected outputs. The fixtures cover common cases but do not include invalid protocols, negative ports, or mixed-family HostIP/podIP beyond meta filtering.

## Test Signals
Provides cross-backend consistency for hostport behavior. Its presence makes backend tests comparable across iptables and nftables.
