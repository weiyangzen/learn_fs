<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_ovs.c -->
# sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_ovs.c

## Purpose
Provides conntrack support routines used outside the normal netfilter hook path, specifically by Open vSwitch and TC conntrack actions. It centralizes helper invocation, TCP sequence adjustment after helper/NAT mangling, network-length trimming, and IPv4/IPv6 fragment reassembly for these callers.

## Important APIs, Types, and Functions
The exported APIs are `nf_ct_helper()`, `nf_ct_add_helper()`, `nf_ct_skb_network_trim()`, and `nf_ct_handle_fragments()`. `nf_ct_helper()` finds the `nf_conn_help` extension, validates helper family and L4 protocol, calls `helper->help()`, then applies `nf_ct_seq_adjust()` when `IPS_SEQ_ADJUST_BIT` is set. `nf_ct_add_helper()` attaches helper state and optionally loads the matching NAT helper. `nf_ct_skb_network_trim()` trims padding based on IPv4 total length or IPv6 payload/HBH length. `nf_ct_handle_fragments()` wraps `ip_defrag()` and `nf_ct_frag6_gather()`.

## Control Flow
OVS/TC callers pass an skb already positioned at the network header. Helper execution skips related replies, connections without helpers, nonmatching families, and nonmatching L4 protocols. IPv4 uses `ip_hdrlen()`; IPv6 skips extension headers and refuses non-first fragments. Fragment handling chooses the per-zone defrag user, clears IP control blocks, gathers fragments, records MRU/next header, clears packet hashes, and sets `ignore_df`.

## State and Persistence
The file stores no durable state. It mutates per-connection helper and sequence-adjust extensions, skb length/hash/control-block fields, and fragment-derived MRU state returned to callers. Helper and NAT helper module references acquired by `nf_ct_add_helper()` persist through the connection helper extension.

## Dependencies and Integration Points
Depends on conntrack helper and seqadj APIs, IPv4/IPv6 defrag, IPv6 extension parsing, and NAT helper loading when enabled. Direct callers include `net/openvswitch/conntrack.c` and `net/sched/act_ct.c`.

## Risks
Incorrect protocol-offset calculation breaks helpers and sequence adjustment. IPv6 extension parsing deliberately ignores later fragments, so callers must defragment before helper inspection where needed. `nf_ct_handle_fragments()` may steal or free skbs, making return-code handling critical. NAT helper loading must stay paired with conntrack helper references.

## Test Signals
Exercise OVS and TC CT actions with FTP/SIP-style helpers, NAT payload mangling, IPv4 fragments, IPv6 fragments, IPv6 HBH padding, unsupported families, and helper module load failures. Packet counters should show drops only on helper failures, seqadj failures, or defrag errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/netfilter/nf_conntrack_ovs.c -->
