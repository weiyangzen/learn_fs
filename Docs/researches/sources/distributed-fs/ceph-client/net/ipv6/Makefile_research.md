# sources/distributed-fs/ceph-client/net/ipv6/Makefile

## Purpose
This Makefile maps IPv6 Kconfig symbols to built-in or modular objects for the Linux INET6 stack. It defines the core `ipv6.o` aggregate and conditionally includes protocol, routing, XFRM, tunnel, offload, netfilter, and utility objects.

## Important APIs, Types, and Functions
The key build variables are `obj-$(CONFIG_IPV6)`, `ipv6-y`, multiple `ipv6-$(CONFIG_...)` fragments, transform modules such as `ah6.o`, `esp6.o`, `ipcomp6.o`, tunnel modules such as `sit.o`, `ip6_tunnel.o`, `ip6_gre.o`, and always/INET-gated objects such as `addrconf_core.o`, `ip6_checksum.o`, `protocol.o`, and `ip6_offload.o`.

## Control Flow
When `CONFIG_IPV6` is enabled, the core aggregate includes AF_INET6, address config, routing, UDP/TCP/RAW/ICMPv6, extension headers, flow labels, Segment Routing, RPL, IOAM, and notifier code. Additional fragments are appended based on sysctl, XFRM, netfilter, procfs, SYN cookies, netlabel, SRv6, RPL, IOAM, and multicast routing symbols. Standalone modules are emitted for IPv6 IPsec transforms and tunnel drivers according to their tristate symbols.

## State and Persistence Behavior
The file has no runtime state; it persists build graph decisions. `obj-$(subst m,y,$(CONFIG_IPV6)) += inet6_hashtables.o` ensures hash-table support is built in when IPv6 is available as built-in or module. Inside the IPv6 guard, UDP tunnel and multicast snooping helpers are added when applicable.

## Dependencies and Integration Points
It must stay aligned with `Kconfig`, source file names, XFRM/INET object dependencies, netfilter subdirectories, and tunnel/offload helper providers shared with IPv4 UDP.

## Risks
Mismatched Kconfig-to-object mapping causes missing symbols or dead code. Core objects included unconditionally under `ipv6-y` must not depend on disabled optional features except through stubs. Module/built-in combinations for IPv6 plus XFRM or UDP tunnel helpers are especially sensitive.

## Test Signals
Run IPv6 disabled, built-in, and module builds; allmodconfig; XFRM on/off; NETFILTER on/off; tunnel feature modules; and link checks for `inet6_hashtables.o`, `ip6_udp_tunnel.o`, and transform modules.
