<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcbpf1_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tcbpf1_kern.c

## Purpose
`tcbpf1_kern.c` is a tc classifier sample that rewrites selected IPv4/TCP packet fields and demonstrates redirect and clone-redirect helpers.

## Important APIs, Types, And Functions
Helpers include `set_dst_mac()`, `set_ip_tos()`, `set_tcp_ip_src()`, and `set_tcp_dest_port()`. Program sections are `classifier`, `redirect_xmit`, `redirect_recv`, `clone_redirect_xmit`, and `clone_redirect_recv`. It uses legacy load helpers, `bpf_skb_store_bytes()`, `bpf_l3_csum_replace()`, `bpf_l4_csum_replace()`, `bpf_redirect()`, and `bpf_clone_redirect()`.

## Control Flow
The classifier reads the IP protocol byte from the skb. For TCP packets it updates TOS, source IP, and destination TCP port while adjusting IP and TCP checksums. Redirect programs send to `skb->ifindex + 1` in transmit or receive direction. Clone redirect programs clone to the neighboring ifindex and then drop the original.

## State And Persistence
There is no map or persistent state. All behavior is per-packet skb mutation or redirection.

## Dependencies And Integration Points
The sample depends on tc cls_bpf, legacy BPF packet load helpers from `bpf_legacy.h`, and Ethernet/IPv4/TCP header layout. It is exercised by tc classifier tests and iproute2 object loading.

## Risks And Edge Cases
The classifier assumes standard Ethernet plus IPv4 header locations and does not explicitly bounds-check headers in C, relying on helper semantics and verifier constraints. The `ifindex + 1` redirect convention is topology-specific. Checksum replacement must match byte order and field sizes.

## Test Signals
Signals include successful tc load, packets rewritten with TOS `8`, source IP `10.1.1.1`, destination port `5001`, and redirect/clone behavior visible in tc counters or peer veth traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tcbpf1_kern.c -->
