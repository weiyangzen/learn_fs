# sources/distributed-fs/ceph-client/net/ipv4/ipcomp.c

## Purpose
Registers IPv4 IP Payload Compression Protocol support for XFRM. It defines the IPv4 IPComp XFRM type, handles ICMP PMTU/redirect errors for compressed packets, initializes IPComp state including tunnel-mode companion IPIP state, and registers the protocol receive hooks.

## APIs, Types, and Functions
The module exposes itself through `module_init(ipcomp4_init)`, `module_exit(ipcomp4_fini)`, and `MODULE_ALIAS_XFRM_TYPE(AF_INET, XFRM_PROTO_COMP)`. Important functions are `ipcomp4_err()`, `ipcomp_tunnel_create()`, `ipcomp_tunnel_attach()`, `ipcomp4_init_state()`, and `ipcomp4_rcv_cb()`. Static registration objects are `ipcomp_type` (`xfrm_type`) and `ipcomp4_protocol` (`xfrm4_protocol`), with a `lock_class_key` for generated tunnel states.

## Control Flow
ICMP errors are filtered to fragmentation-needed and redirects, the CPI is converted into an XFRM SPI, and matching COMP state is looked up using skb mark, destination, SPI, protocol, and AF_INET. PMTU or redirect updates are then delegated to IPv4 route/XFRM helpers. State initialization allows transport mode directly and tunnel mode with extra IPv4 header length. Generic `ipcomp_init_state()` sets compression details; tunnel mode additionally attaches or creates a companion IPIP XFRM state under `xfrm_cfg_mutex`.

## State and Persistence
Registered XFRM type/protocol entries persist for the module lifetime. For tunnel mode, `x->tunnel` points to a companion IPIP `xfrm_state`; that state has copied selector, addresses, family, mode, flags, mark, if_id, initialized lock class, and incremented `tunnel_users`. State reference counts are deliberately held to represent tunnel use and are released by generic XFRM/IPComp destruction paths.

## Dependencies and Integration
Depends on XFRM type/protocol registration, generic IPComp input/output/destructor helpers, IPv4 ICMP route update helpers, XFRM state allocation/lookup/insert/reference handling, rtnetlink locking context, and the IPIP protocol model used as the tunnel wrapper for compressed tunnel-mode traffic.

## Risks
Risks include incorrect CPI-to-SPI mapping, companion tunnel state leaks or reference imbalance, unsupported mode handling, lock-class assumptions, PMTU updates with insufficient ICMP payload, and registration failure cleanup. Compression algorithm behavior and adaptive tuning are explicitly outside this file and noted as TODOs.

## Test Signals
Signals include XFRM state add/delete for IPComp transport and tunnel mode, failure paths for unsupported modes or missing companion state, compressed packet input/output, ICMP fragmentation-needed PMTU propagation, redirect handling, module load/unload registration order, and reference tracking of `tunnel_users`.
