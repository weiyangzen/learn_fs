<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_redirect_map.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_redirect_map.c

## Purpose
This XDP program suite supports redirect-map tests by redirecting to fixed devmap entries, counting received IPv4 packets, and storing source MAC addresses.

## Important APIs, Types, and Functions
It declares `tx_port` devmap, `rxcnt` array counter map, and `rx_mac` array map. Entry points are `xdp_redirect_map_0/1/2`, `xdp_count_0/1/2`, and `store_mac_1/2`; helpers include `bpf_redirect_map`, `bpf_map_lookup_elem`, `bpf_map_update_elem`, and `bpf_printk`.

## Control Flow
Redirect programs immediately redirect to a fixed devmap key. Counting programs validate Ethernet header bounds, increment per-key counters only for IPv4, and pass. MAC storage programs validate Ethernet, copy IPv4 source MAC into a 64-bit map value, log with `bpf_printk`, and pass.

## State and Persistence
Devmap entries are populated by userspace. `rxcnt` persists packet counts and `rx_mac` persists observed source MACs.

## Dependencies and Integration Points
It integrates with XDP redirect selftests that configure devmaps, attach different programs to devices, and inspect maps after traffic.

## Risks
Counters use non-atomic `*count += 1`; tests should avoid high-concurrency ambiguity. Only IPv4 packets affect counters/MAC storage.

## Test Signals
Successful redirects return XDP redirect actions via helper; map counters and stored MACs confirm traffic path and receiving interface behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/xdp_redirect_map.c -->
