<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_router_ipv4_user.c -->
# sources/distributed-fs/ceph-client/samples/bpf/xdp_router_ipv4_user.c

## Purpose
`xdp_router_ipv4_user.c` is the control plane and stats UI for the XDP IPv4 router sample. It loads the BPF skeleton, attaches XDP programs, mirrors kernel route and ARP state into BPF maps via netlink, and runs the shared XDP sample statistics loop.

## Important APIs, Types, And Functions
Important routines are `recv_msg()`, `read_route()`, `get_route_table()`, `read_arp()`, `get_arp_table()`, `monitor_routes_thread()`, `usage()`, and `main()`. It uses netlink route/neighbour messages, `bpf_map_update_elem()`, `bpf_map_delete_elem()`, `sample_init_pre_load()`, `sample_init()`, `sample_install_xdp()`, `sample_run()`, and skeleton APIs from `xdp_router_ipv4.skel.h`.

## Control Flow
Startup opens and loads the skeleton, initializes shared stats maps and tracepoint attachments, parses options, resolves router maps, attaches XDP to each interface, starts a route-monitor thread, and runs the stats loop. The monitor thread dumps initial ARP and route tables, subscribes to route and neighbour multicast groups, and updates `lpm_map`, `exact_match`, `arp_table`, and `tx_port` as messages arrive.

## State And Persistence
Userspace maintains map fds, route-monitor thread state, interval, and sample stats state. BPF maps hold mirrored route, exact host, ARP, and devmap state. XDP programs remain attached until `sample_exit()` cleanup.

## Dependencies And Integration Points
It depends on libbpf skeleton generation, pthreads, netlink route/neighbour APIs, shared XDP sample helpers, interface MAC lookup, and kernel XDP support. It integrates host routing state with fast-path BPF forwarding.

## Risks And Edge Cases
Route parsing uses string buffers and `atoi()` on binary addresses, making formatting fragile. Option parsing adjusts `ifname_list` manually and can be error-prone. Route deletion triggers a full route-table reread for same-prefix replacement. Netlink polling intervals can delay updates.

## Test Signals
Successful runs attach to all named interfaces, populate maps from existing routes/ARP, print XDP sample stats, and update forwarding behavior after route or neighbour changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/samples/bpf/xdp_router_ipv4_user.c -->
