<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_user.c

## Purpose
`xdp_tx_iptunnel_user.c` loads the XDP tunnel transmit sample, populates VIP-to-tunnel mappings from command-line arguments, attaches the XDP program, and prints per-protocol encapsulation rates.

## Important APIs, Types, And Functions
Key routines are `int_exit()`, `poll_stats()`, `usage()`, `parse_ipstr()`, `parse_ports()`, and `main()`. It uses `inet_pton()`, `ether_aton_r()`, `bpf_object__open_file()`, `bpf_program__set_type()`, `bpf_object__load()`, `bpf_map_update_elem()`, `bpf_xdp_attach()`, `bpf_xdp_query_id()`, and `bpf_xdp_detach()`.

## Control Flow
The program requires interface, VIP address, port/range, tunnel source/destination, and destination MAC. It validates IP families, opens `<argv[0]>_kern.o`, loads the XDP program, resolves `rxcnt` and `vip2tnl`, inserts one map entry for each port in the range, attaches XDP, records program id, and polls per-protocol counters until timeout or signal.

## State And Persistence
State includes attached XDP program id, `vip2tnl` entries, `rxcnt` counters, and local previous-counter snapshots. Signal cleanup detaches only if the attached program id matches.

## Dependencies And Integration Points
It depends on libbpf, XDP attach support, valid interface/MAC/IP arguments, and the shared common header layout.

## Risks And Edge Cases
`parse_ports()` references `optarg` instead of its parameter internally, which is safe for current call sites but fragile. The map capacity limits port ranges to 256 entries. Family mismatch between tunnel source and destination is rejected, but VIP and tunnel family compatibility is enforced by the BPF side.

## Test Signals
After attach, matching traffic should produce periodic `proto <n>` packet/rate lines. Cleanup should remove the program unless another XDP program replaced it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_tx_iptunnel_user.c -->
