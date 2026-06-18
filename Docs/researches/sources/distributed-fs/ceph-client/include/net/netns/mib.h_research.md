# sources/distributed-fs/ceph-client/include/net/netns/mib.h

Purpose: Defines per-network-namespace SNMP/MIB statistics pointers for core IP, ICMP, TCP, UDP, and Linux-specific networking counters.

Important APIs/types/functions: `struct netns_mib` contains per-cpu stat pointers such as IP, IPv6, ICMP, ICMPv6, TCP, UDP, UDPLite, Linux MIB, and IPv6 fragment stats depending on config.

Control flow: Protocol paths increment per-cpu counters through MIB macros; procfs/netlink stats readers aggregate them.

State and persistence: Runtime per-net per-cpu counters, allocated during namespace initialization and freed on teardown.

Dependencies/integration: Depends on SNMP stat definitions, protocol config options, procfs/stat readers, and per-cpu allocation.

Risks/test signals: Test allocation/cleanup for config matrices, counter increments under concurrency, namespace isolation in `/proc/net/snmp*`, and disabled protocol configs.
