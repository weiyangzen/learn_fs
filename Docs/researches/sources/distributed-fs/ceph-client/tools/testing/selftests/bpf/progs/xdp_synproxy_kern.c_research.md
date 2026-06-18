<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_synproxy_kern.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_synproxy_kern.c

## Purpose
This XDP/tc SYN proxy program implements SYN-cookie based TCP SYN flood protection for IPv4 and IPv6, using conntrack lookup to pass established flows and generating SYNACK packets for allowed ports.

## Important APIs, Types, and Functions
Maps are `values` for packed MSS/window-scale/TTL and SYNACK count, and `allowed_ports` for port allowlist. It declares conntrack kfuncs `bpf_xdp_ct_lookup`, `bpf_skb_ct_lookup`, and `bpf_ct_release`. Helpers/kfuncs include `bpf_tcp_raw_gen_syncookie_ipv4/ipv6`, `bpf_tcp_raw_check_syncookie_ipv4/ipv6`, `bpf_csum_diff`, `bpf_xdp_adjust_tail`, `bpf_skb_change_tail`, `bpf_redirect`, and `bpf_loop`.

## Control Flow
Packet processing starts in `syncookie_xdp` or `syncookie_tc`. `syncookie_part1` dissects Ethernet/IP/TCP, checks conntrack, rejects non-SYN/non-ACK unknown flows, and grows tail room to `TCP_MAXLEN`. `syncookie_part2` refreshes pointers after tail adjustment, validates TCP length, then dispatches SYNs to `syncookie_handle_syn` or ACKs to `syncookie_handle_ack`. SYN handling verifies checksums, checks allowed destination ports, generates a raw syncookie, parses timestamp/SACK/window-scale options with bounded `bpf_loop`, rewrites Ethernet/IP/TCP into a SYNACK, recalculates checksums, adjusts tail length, increments the SYNACK counter, and returns XDP_TX or tc redirect. ACK handling verifies the cookie and passes only valid ACKs.

## State and Persistence
Persistent state is in the `values` map and `allowed_ports` map. The SYNACK counter is incremented atomically at key 1. Packet state is heavily mutated for SYNACK generation, including MAC/IP/port swaps, TCP flags/options, sequence/ack numbers, checksums, and packet length.

## Dependencies and Integration Points
The program integrates with XDP and tc selftests for SYN proxy behavior and requires conntrack BPF kfuncs plus raw TCP syncookie helpers. It depends on `vmlinux.h`, `bpf_compiler.h`, endian helpers, and kernel networking definitions.

## Risks
The code intentionally does not support VLANs, IPv6 extension headers, or fragmented TCP in XDP, and comments identify those bypasses. It relies on verifier-sensitive constructs such as volatile pointers and bounded loops. Incorrect checksum or tail adjustment logic would drop or corrupt packets. Conntrack module configuration can affect kfunc availability.

## Test Signals
Allowed SYNs should produce SYNACK TX/redirect and increment the SYNACK counter, valid cookie ACKs should pass, established conntrack flows should pass, blocked ports/bad checksums/fragments should drop, and malformed verifier-sensitive paths should not fail load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_synproxy_kern.c -->
