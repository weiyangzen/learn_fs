# sources/distributed-fs/ceph-client/net/ipv6/Kconfig

## Purpose
This Kconfig file defines the IPv6 protocol configuration menu and feature symbols for IPv6 routing, address behavior, IPsec transforms, tunnels, multicast routing, Segment Routing, RPL, IOAM, FoU, ILA, and related dependencies.

## Important APIs, Types, and Functions
The important "API" is the set of configuration symbols: `IPV6`, `IPV6_ROUTER_PREF`, `IPV6_ROUTE_INFO`, `IPV6_OPTIMISTIC_DAD`, `INET6_AH`, `INET6_ESP`, `INET6_ESP_OFFLOAD`, `INET6_ESPINTCP`, `INET6_IPCOMP`, `IPV6_MIP6`, `IPV6_ILA`, `INET6_XFRM_TUNNEL`, `INET6_TUNNEL`, `IPV6_VTI`, `IPV6_SIT`, `IPV6_SIT_6RD`, `IPV6_TUNNEL`, `IPV6_GRE`, `IPV6_FOU`, `IPV6_MULTIPLE_TABLES`, multicast routing symbols, `IPV6_SEG6_*`, `IPV6_RPL_LWTUNNEL`, and `IPV6_IOAM6_LWTUNNEL`.

## Control Flow
The top-level `menuconfig IPV6` gates all nested options. Symbols express dependency and selection flow: IPsec transforms select generic XFRM crypto pieces, tunnel features select tunnel and dst-cache support, route-policy features select `FIB_RULES`, and Segment Routing/IOAM/RPL select lightweight tunnel and cache infrastructure.

## State and Persistence Behavior
Kconfig choices persist in the kernel `.config` and drive compile-time object inclusion. Defaults matter: IPv6 defaults on, SIT defaults module, several tunnel/offload helpers default from other networking symbols, and many advanced options default off.

## Dependencies and Integration Points
The file coordinates with IPv6 Makefile object selection, crypto API, XFRM, netfilter, lightweight tunnels, dst cache, multicast routing, GRE demux, FoU, stream parser, sockmap messaging, and documentation.

## Risks
Incorrect dependencies can allow link failures or silently omit required helpers. Over-broad `select` statements can force features unexpectedly. Defaulting IPv6 on affects build footprint for kernels using this source tree.

## Test Signals
Use randconfig/allmodconfig builds, targeted configs for each tunnel/IPsec feature, dependency checks with NETFILTER/XFRM disabled, module/built-in combinations, and verification that selected objects in the IPv6 Makefile match enabled symbols.
