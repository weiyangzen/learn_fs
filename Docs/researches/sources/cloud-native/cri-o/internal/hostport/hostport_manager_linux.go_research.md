# sources/cloud-native/cri-o/internal/hostport/hostport_manager_linux.go

## Purpose
Provides Linux-specific deletion of UDP conntrack entries for hostport destination ports after new NAT rules are installed.

## Important APIs, Types, And Functions
- `deleteConntrackEntriesForDstPort(port uint16, protocol uint8, family netlink.InetFamily) error` builds a `netlink.ConntrackFilter` and calls `netlink.ConntrackDeleteFilters`.

## Control Flow
The function adds protocol and original destination port filters, then deletes matching entries from the conntrack table for the specified address family. Each setup/delete error is wrapped with protocol and port context.

## State And Persistence
Mutates kernel conntrack state by deleting entries. It does not alter iptables/nftables rules or CRI-O state.

## Dependencies And Integration Points
Used by `metaHostportManager.Add` for UDP hostports after backend Add succeeds. Depends on `vishvananda/netlink` and Linux netfilter conntrack support.

## Risks And Edge Cases
Deletion requires suitable privileges and kernel support. Errors are logged but ignored by the meta manager, so stale conntrack entries may remain and temporarily blackhole UDP traffic.

## Test Signals
No direct unit test in this subset because it touches kernel conntrack. Behavior is indirectly represented by meta-manager code paths.
