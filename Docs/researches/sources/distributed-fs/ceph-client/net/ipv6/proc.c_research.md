# sources/distributed-fs/ceph-client/net/ipv6/proc.c

Purpose: Implements IPv6 procfs statistics files: `/proc/net/sockstat6`, `/proc/net/snmp6`, and per-device `/proc/net/dev_snmp6/<dev>`.

Important APIs, types, and functions: `sockstat6_seq_show()` reports TCP6/UDP6/RAW6 socket usage and fragment cache usage. SNMP item arrays map visible names to IPv6, ICMPv6, and UDPv6 MIB entries. `snmp6_seq_show_item()`, `snmp6_seq_show_item64()`, and `snmp6_seq_show_icmpv6msg()` render counters. `snmp6_register_dev()` and `snmp6_unregister_dev()` manage per-device proc entries. `ipv6_misc_proc_init()` and `ipv6_misc_proc_exit()` register pernet proc lifecycle.

Control flow: Per-net init creates `sockstat6`, `snmp6`, then `dev_snmp6`, unwinding earlier entries on failure. `snmp6` rendering emits per-net IPv6 stats, ICMPv6 base stats, ICMPv6 message stats, and UDPv6 stats. Device rendering emits `ifIndex`, per-device IPv6 stats, per-device ICMPv6 stats excluding the host rate-limit item, and message stats. Per-net exit removes all entries.

State and persistence: Proc entries are per-net; device entries are stored in `idev->stats.proc_dir_entry`. Counter state lives in per-net/per-device MIB allocations and is only read here. No persistent storage.

Dependencies and integration: Depends on procfs seq APIs, network namespace lifecycle, IPv6 device state, SNMP counter batching helpers, and socket protocol in-use accounting for `tcpv6_prot`, `udpv6_prot`, and `rawv6_prot`.

Risks and test signals: Risks include proc entry lifetime during device/netns teardown, counter batching consistency, missing directories, and name formatting compatibility. Tests should create/destroy netns and IPv6 devices, read all proc files while traffic updates counters, verify failure unwinds with fault injection, and compare output names against expected userspace parsers.
