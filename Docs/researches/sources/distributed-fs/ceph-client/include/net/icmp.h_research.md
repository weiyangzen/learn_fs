# sources/distributed-fs/ceph-client/include/net/icmp.h

Purpose: declares IPv4 ICMP error/reporting interfaces and statistics macros. It lets IP and transport protocols send ICMP errors, handle received ICMP, convert ICMP errors to errno/fatal state, and maintain per-net ICMP counters.

Important APIs/types: `struct icmp_err` maps ICMP codes to `errno` and fatality; `icmp_err_convert[]` is the exported table. Stats macros increment ICMP and per-message counters. `__icmp_send()` is the main send helper with mark override; `icmp_send()` wraps it with zero mark. `icmp_ndo_send()` has a real or stub implementation depending on `CONFIG_IP_ROUTE_NH_FDB`. Receive/error/init functions include `icmp_rcv()`, `icmp_err()`, `icmp_init()`, `icmp_out_count()`, and `icmp_build_probe()`.

Control flow and state: protocols call send helpers when rejecting packets or reporting path errors. Receive path dispatches ICMP to error handlers and updates counters. State is per-network-namespace SNMP MIB data plus socket/error side effects.

Dependencies and integration: depends on Linux ICMP UAPI, `inet_sock.h`, SNMP, and `ip.h`. It integrates with IPv4 input/output, route error handling, PMTU discovery, and transport error queues.

Risks: ICMP generation must avoid loops, respect rate limits elsewhere, and preserve marks where needed. Tests should cover stats increments, errno mapping, PMTU errors, `icmp_ndo_send()` config variants, probe building, and malformed ICMP receive packets.
