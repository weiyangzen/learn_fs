<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/snmp.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/snmp.h

Purpose: defines numeric MIB counter indexes for Linux networking SNMP/proc statistics across IP, ICMP, ICMPv6, TCP, UDP, and Linux-specific protocol counters.

Important APIs, types, and functions: enums export `IPSTATS_MIB_*`, `ICMP_MIB_*`, `ICMP6_MIB_*`, `TCP_MIB_*`, `UDP_MIB_*`, and many `LINUX_MIB_*` counters. `__ICMPMSG_MIB_MAX` and `__ICMP6MSG_MIB_MAX` size per-message-type arrays. Comments map many counters to RFC MIB names and Linux `/proc/net/snmp`/`netstat` labels.

Control flow: kernel networking fast paths increment per-CPU MIB counters by enum index. Procfs/sysctl/netlink readers aggregate and format counters for userspace monitoring.

State and persistence behavior: counters are runtime per-network-namespace/per-CPU statistics. They reset on namespace or system lifetime and are not persistent. The header defines indexes only.

Dependencies and integration points: integrates with IPv4/IPv6, ICMP, TCP, UDP, MIB aggregation, `/proc/net/snmp`, `/proc/net/netstat`, SNMP agents, and monitoring tools.

Risks and edge cases: enum ordering is ABI-sensitive for array indexes and proc output mapping. Fast-path counters are grouped partly for cache behavior. Adding counters must update string tables and max values consistently.

Test signals: compare procfs counter names/counts with enum tables, run packet-level tests that increment representative counters, verify per-netns isolation, and compile-check string table alignment with max enum values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/snmp.h -->
