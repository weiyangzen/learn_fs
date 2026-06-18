# sources/distributed-fs/ceph-client/include/uapi/linux/netfilter/nf_conntrack_common.h

## Purpose
Defines common netfilter connection tracking UAPI states, status bits, event IDs, expectation events, and expectation flags.

## Important APIs, Types, And Functions
Exports `ip_conntrack_info`, state-bit macros `NF_CT_STATE_*`, `ip_conntrack_status`, `ip_conntrack_events`, `ip_conntrack_expect_events`, and expectation flags `NF_CT_EXPECT_*`.

## Control Flow
Conntrack classifies packets as new, related, established, reply-direction, invalid, or untracked. Status bits mark lifecycle and NAT/helper/offload conditions. Netlink/event consumers receive state/status updates by event ID.

## State, Persistence, And Dependencies
State persists in conntrack entries, expectations, NAT status, helper/offload markers, and event streams. No external dependencies.

## Integration Points
Used by nftables/iptables ct matches, ctnetlink, NAT, helpers, flow offload, and userspace conntrack tools.

## Risks
Some bits are unchangeable from userspace and some have in-kernel repurposing under `__KERNEL__`. Reply-direction arithmetic underlies state bit macros and must be preserved.

## Test Signals
Validate state bit expansion, NAT done/mask behavior, event emission, helper/offload bits, expectation flags, and userspace attempts to modify unchangeable bits.
