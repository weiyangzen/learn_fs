# sources/distributed-fs/ceph-client/net/netfilter/Kconfig

## Purpose

This Kconfig file is the main configuration surface for the kernel netfilter stack under `net/netfilter`. It gates ingress and egress hooks, nfnetlink interfaces, connection tracking, NAT, nf_tables, flow tables, xtables targets, xtables matches, and then includes the ipset and IPVS submenus. It is a build-time policy document rather than runtime code, but it directly controls which modules from the neighboring Makefile can be built and which symbols other networking code may rely on.

## Important Symbols And Dependencies

The top-level menu depends on `INET && NETFILTER`. Early symbols enable core hook families and integration points: `NETFILTER_INGRESS` selects `NET_INGRESS`, `NETFILTER_EGRESS` selects `NET_EGRESS`, `NETFILTER_SKIP_EGRESS` is enabled when egress hooks coexist with `NET_CLS_ACT` or `IFB`, and `NETFILTER_BPF_LINK` follows `BPF_SYSCALL`. The nfnetlink options select `NETFILTER_NETLINK` for accounting, queueing, logging, OS fingerprinting, and base hook dump support.

`NF_CONNTRACK` selects IPv4 defragmentation and IPv6 defragmentation when IPv6 is present. Its nested options control marks, secmarks, zones, procfs export, events, timeout extension, timestamps, labels, protocol helpers, and application helpers. `NF_NAT` depends on conntrack and has helper-specific defaults that mirror the corresponding conntrack helper.

`NF_TABLES` selects `NETFILTER_NETLINK` and `NET_CRC32C`, then exposes nftables families and expressions such as CT, flow offload, NAT, queue, quota, reject, compat, fib, socket, OSF, tproxy, xfrm, synproxy, and flow table support. `NETFILTER_XTABLES` exposes legacy x_tables plus many targets and matches, with dependencies that pull in conntrack, NAT, textsearch, socket lookup, bridge, XFRM, LED, IPVS, and protocol-specific features.

## Control Flow And State

Kconfig evaluation determines the symbol graph. Many options are only visible with `NETFILTER_ADVANCED`; when advanced mode is off, several common modules default to `m`, preserving common firewall functionality without exposing the full menu. Nested `if NF_CONNTRACK`, `if NF_TABLES`, and `if NETFILTER_XTABLES` blocks shape the feature families and ensure impossible combinations are not presented. The final `source` lines include `net/netfilter/ipset/Kconfig` and `net/netfilter/ipvs/Kconfig`, so ipset and IPVS are subordinate configuration trees.

The file has no runtime persistence, but selected symbols persist in `.config` and become ABI-affecting build inputs. Defaults such as `CONFIG_NF_CONNTRACK=m`, `CONFIG_NETFILTER_NETLINK_LOG=m`, and many xtables defaults in non-advanced mode influence which modules are available on a deployed system.

## Integration Points

The file integrates with `net/netfilter/Makefile`, which maps these symbols to objects. It also integrates with IPv4/IPv6 Kconfig trees through dependencies such as `IP_NF_RAW`, `IP6_NF_RAW`, `NF_TABLES_IPV4`, and `NF_TABLES_IPV6`; with tc/netdev through ingress and egress; with BPF through `NETFILTER_BPF_LINK`; with XFRM, IPVS, bridge netfilter, textsearch, LED triggers, and lwtunnel through conditional symbols.

## Risks

The main risk is dependency drift: adding an object in the Makefile without a matching Kconfig symbol, or adding a symbol here without the needed `select`/`depends on`, can create link failures or unusable modules. Defaults under `NETFILTER_ADVANCED=n` are security-sensitive because they quietly build packet filtering, logging, conntrack, and NAT helpers. Another risk is hidden feature coupling: many xtables targets select helper modules, defragmentation, or NAT subfeatures, so changing one dependency can break runtime rules that appear unrelated.

## Test Signals

Useful signals are `make olddefconfig`, `make allmodconfig`, and targeted builds for `net/netfilter/`. Runtime smoke tests should exercise nf_tables, xtables, nfqueue/nflog, conntrack, NAT, ingress/egress hook registration, and ipset/IPVS menus under common IPv4-only, IPv6, and module/built-in configurations.
