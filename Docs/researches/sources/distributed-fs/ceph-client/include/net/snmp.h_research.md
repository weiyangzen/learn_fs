# sources/distributed-fs/ceph-client/include/net/snmp.h

## Purpose
This header defines kernel-side SNMP/MIB statistic storage wrappers and update macros for IP, ICMP, TCP, UDP, Linux, XFRM, and TLS networking counters.

## Important APIs, Types, And Functions
It defines `struct snmp_mib` name/entry descriptors and per-protocol MIB wrapper structs with arrays sized from UAPI enums, including `ipstats_mib`, `icmp_mib`, `icmpmsg_mib`, `icmpv6_mib`, device variants, `tcp_mib`, `udp_mib`, `linux_mib`, `linux_xfrm_mib`, and `linux_tls_mib`. Macros define per-cpu or atomic stat declarations and update helpers: `DEFINE_SNMP_STAT`, `DECLARE_SNMP_STAT`, `SNMP_INC_STATS`, `SNMP_DEC_STATS`, `SNMP_ADD_STATS`, packet/octet pair updates, and 64-bit variants using `u64_stats` synchronization on 64-bit stat builds.

## Control Flow
Protocol code updates per-net/per-cpu counters through macros. `/proc` and seq-file export code reads these arrays and maps entries to names using MIB descriptors.

## State And Persistence
Counters persist in per-net protocol statistic storage, often per-cpu for low overhead. 64-bit updates use synchronization to avoid torn reads.

## Dependencies And Integration Points
It depends on Linux SNMP UAPI enums, SMP/per-cpu support, cache alignment, and `u64_stats`. SCTP and other protocols wrap these macros for their own MIBs.

## Risks And Test Signals
Risks include wrong enum sizing, torn 64-bit stats, per-cpu aggregation mistakes, atomic/per-cpu mismatch, and packet/octet pair update inconsistencies. Test signals include `/proc/net/snmp` and related proc outputs, protocol counter increments under traffic, 32-bit build reads, and namespace-specific statistics.
