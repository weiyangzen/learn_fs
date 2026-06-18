# sources/distributed-fs/ceph-client/net/netfilter/ipvs/ip_vs_proto.c

## Purpose
Implements the core IPVS protocol registry and per-netns protocol data setup. It registers protocol handlers for TCP, UDP, SCTP, AH, and ESP, provides lookup helpers, forwards timeout-change events, and supplies shared TCP/UDP packet debug formatting.

## Important APIs, Types, and Functions
Global registration uses `register_ip_vs_protocol()` and `unregister_ip_vs_protocol()` over `ip_vs_proto_table`. Per-netns data uses `register_ip_vs_proto_netns()` and `unregister_ip_vs_proto_netns()` with `struct ip_vs_proto_data`. Exported lookups are `ip_vs_proto_get()` and `ip_vs_proto_data_get()`. `ip_vs_protocol_timeout_change()` invokes each protocol's timeout-change hook. `ip_vs_state_name()` formats connection state names, and `ip_vs_tcpudp_debug_packet()` prints IPv4/IPv6 packet endpoint details.

## Control Flow
IPVS module init calls `ip_vs_protocol_init()`, registering compiled-in protocol structures and logging their names. Each network namespace calls `ip_vs_protocol_net_init()`, which allocates `ip_vs_proto_data` for each compiled protocol and lets the protocol initialize timeout tables or app lists. Cleanup walks each hash bucket and unregisters all per-netns data, then module cleanup removes global handlers.

## State and Persistence
Global protocol state is a fixed 32-bucket hash table keyed by protocol number. Per-netns state is stored in `netns_ipvs->proto_data_table`, including protocol-specific timeout tables, app counters, and app lists. State persists for the lifetime of the module or network namespace.

## Dependencies and Integration Points
Depends on compiled protocol objects from `ip_vs_proto_tcp.c`, `ip_vs_proto_udp.c`, `ip_vs_proto_sctp.c`, and `ip_vs_proto_ah_esp.c`. It integrates with connection creation, packet scheduling, app helpers, state-name reporting, sysctl timeout propagation, and proc/debug output.

## Risks
The global protocol table is intentionally unlocked because registration occurs only during module load/unload; adding dynamic protocol modules would require synchronization. Per-netns initialization must unwind correctly on allocation failure. The protocol log buffer is fixed at 64 bytes and assumes the compiled protocol list fits. Debug packet parsing has limited IPv6 extension-header awareness and reports fragments specially.

## Test Signals
Verify protocol registration logs, lookup by protocol number, netns creation and teardown, timeout table allocation failures, protocol cleanup unloading all handlers, `ip_vs_state_name()` for templates and unknown protocols, and debug output for truncated, fragmented, IPv4, and IPv6 packets.
