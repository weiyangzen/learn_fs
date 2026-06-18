# sources/distributed-fs/ceph-client/net/ipv4/proc.c

## Purpose
Implements IPv4-related procfs statistics for each network namespace: `/proc/net/sockstat`, `/proc/net/snmp`, and `/proc/net/netstat`.

## Important APIs, types, and functions
`sockstat_seq_show()` prints socket allocation and memory. Static MIB arrays map visible names to IP/TCP/UDP/ICMP/Linux counter indexes. `icmpmsg_put()`, `icmp_put()`, `snmp_seq_show_ipstats()`, `snmp_seq_show_tcp_udp()`, `snmp_seq_show()`, and `netstat_seq_show()` format output. `ip_proc_init_net()` and `ip_proc_exit_net()` manage proc entries; `ip_misc_proc_init()` registers pernet operations.

## Control flow
Namespace init creates `sockstat`, `netstat`, and `snmp` with rollback on partial failure. Reads invoke seq_file callbacks. SNMP output prints header/value pairs and uses batched per-cpu counter collection. ICMP message counters print only nonzero values in batches. Netstat allocates a temporary buffer for batched extended counters and falls back to folded reads on allocation failure, then appends MPTCP stats.

## State and persistence
The file owns no counters. It reads live per-net MIB structures, protocol memory accounting, socket in-use counters, TCP timewait counts, and fragment table state. Proc entries are per namespace and removed at exit.

## Dependencies and integration points
Integrates with procfs, seq_file, pernet operations, TCP/UDP/RAW accounting, ICMP/IP SNMP counters, MPTCP stats, fragment memory accounting, and namespace proc roots.

## Risks
Output format is user ABI for monitoring tools, so counter names/order are compatibility-sensitive. Counter batching must respect per-cpu synchronization. Partial proc creation rollback must remove only created entries.

## Test signals
Read all three proc files in init and non-init namespaces, verify header/value alignment, exercise allocation fallback, generate protocol traffic and check counters, and test cleanup on namespace deletion.
