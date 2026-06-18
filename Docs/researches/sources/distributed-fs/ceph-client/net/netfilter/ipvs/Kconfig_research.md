# sources/distributed-fs/ceph-client/net/netfilter/ipvs/Kconfig

## Purpose

`Kconfig` defines the build-time configuration surface for IP Virtual Server support. It gates the core IPVS module, protocol support, scheduler modules, application helpers, netfilter conntrack integration, persistence engines, debug support, IPv6 support, and hash-table sizing options.

## Important APIs, types, and functions

The central symbol is `IP_VS`, a tristate depending on `INET`, `NETFILTER`, and compatible `NF_CONNTRACK` state. `IP_VS_IPV6` adds IPv6 support and selects `NF_DEFRAG_IPV6`. `IP_VS_DEBUG` enables debug logging controlled at runtime by the IPVS sysctl. `IP_VS_TAB_BITS` configures the connection table size exponent, with architecture-dependent ranges. Protocol symbols include TCP, UDP, ESP/AH, and SCTP. Scheduler symbols include RR, WRR, LC, WLC, FO, OVF, LBLC, LBLCR, DH, SH, MH, SED, NQ, and TWOS. Helper symbols include `IP_VS_FTP`, `IP_VS_NFCT`, and `IP_VS_PE_SIP`.

## Control flow

Kconfig presents `IP_VS` as a menu. When disabled, all nested options are hidden. Enabling it exposes transport protocol choices, scheduler choices, SH/MH table sizing, application helper selection, connection tracking export, and SIP persistence. Dependencies enforce that FTP helper support is only available with TCP, conntrack, NAT, and FTP conntrack support; SIP persistence depends on UDP and SIP conntrack.

## State and persistence behavior

This file has no runtime state. Its selected symbols become compile-time configuration that controls which object files are built, which code branches compile, default connection table size, and which dependencies are selected.

## Dependencies and integration points

It integrates with the kernel Kconfig system and the adjacent IPVS Makefile. Runtime files such as `ip_vs_conn.c` read `CONFIG_IP_VS_TAB_BITS`, `CONFIG_IP_VS_IPV6`, `CONFIG_SYSCTL`, and protocol/helper symbols to include or exclude functionality.

## Risks

Incorrect dependencies can build modules without required protocol, NAT, conntrack, or defragmentation support. `IP_VS_TAB_BITS` has memory and performance implications; too small increases collision cost, too large wastes memory. Some scheduler/help text is user-facing, so symbol naming and dependency clarity affect configuration usability.

## Test signals

Tests are mostly build-matrix checks: core built-in/module/disabled, IPv6 enabled/disabled, each protocol and scheduler as module, FTP helper dependency failures, SIP persistence dependencies, conntrack export, and boundary values for `IP_VS_TAB_BITS`, `IP_VS_SH_TAB_BITS`, and `IP_VS_MH_TAB_INDEX`.
