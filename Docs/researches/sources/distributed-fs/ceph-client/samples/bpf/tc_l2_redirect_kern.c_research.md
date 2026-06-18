<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect_kern.c -->
# sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect_kern.c

## Purpose
`tc_l2_redirect_kern.c` contains tc classifier programs that redirect selected L2 frames into IPIP/IP6 tunnel devices and drop non-tunneled traffic to configured VIP prefixes. It demonstrates `bpf_skb_set_tunnel_key()`, `bpf_redirect()`, ingress redirection, pinned maps, and packet parsing in cls_bpf.

## Important APIs, Types, And Functions
The pinned `tun_iface` array map stores the tunnel ifindex. `is_vip_addr()` matches IPv4 `10.10.1.0/24` and IPv6 `2401:face::/` prefix fragments. Program sections are `l2_to_iptun_ingress_forward`, `l2_to_iptun_ingress_redirect`, `l2_to_ip6tun_ingress_redirect`, and `drop_non_tun_vip`.

## Control Flow
Each tc program validates Ethernet and IP header bounds before reading packet fields. The forward section recognizes tunneled IP/IP6 packets and redirects them to the configured tunnel with `BPF_F_INGRESS`. Redirect sections match VIP destinations, fill a `bpf_tunnel_key` for IPv4 or IPv6 remote tunnel endpoints, call `bpf_skb_set_tunnel_key()`, and redirect to the tunnel ifindex. The drop section drops VIP-bound packets that are not accepted through the tunnel path.

## State And Persistence
The only persistent BPF state is the pinned single-entry `tun_iface` map updated by userspace. Packet mutations are transient per skb. Trace messages are emitted with `bpf_trace_printk()` for diagnostics.

## Dependencies And Integration Points
The program depends on tc clsact, BPF helper support for tunnel keys and redirect, iproute2 ELF map pinning, and the shell/user helpers. It integrates with Linux tunnel devices whose ifindex is shared through the map.

## Risks And Edge Cases
Header parsing must remain verifier-safe and correctly account for Ethernet/IP header sizes. The code assumes simple non-fragmented IPv4/IPv6 headers and fixed VIP/tunnel addresses. Missing map values silently pass packets, and bad ifindex values can blackhole traffic. `bpf_trace_printk()` is diagnostic-only and expensive under load.

## Test Signals
Expected signals are successful verifier load for all sections, correct redirect counters in `tc -s`, successful pings through IPIP/IP6 tunnels, VIP drops for non-tunnel packets, and trace output showing selected redirect/forward decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/tc_l2_redirect_kern.c -->
