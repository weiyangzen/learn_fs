# sources/distributed-fs/ceph-client/net/ipv4/Makefile

## Purpose
The IPv4 Makefile maps core IPv4 stack components and optional features to kbuild objects.

## Important APIs, types, and functions
The `obj-y` list builds core routing, protocol, TCP, UDP, ARP, ICMP, device address, FIB, fragmentation, ping, tunnel-core, offload, metrics, netlink, nexthop, and stub objects. Optional `obj-$(CONFIG_...)` entries cover tunnels, sysctl/proc, FIB rules, multicast routing, IPsec transforms, netfilter, INET diagnostics, raw/UDP/TCP diag modules, congestion-control modules, TCP signature pool, BPF UDP/TCP pieces, NetLabel CIPSO, XFRM IPv4 support, and TCP-AO.

## Control flow
Kbuild evaluates the object lists from the generated config. Composite objects are defined for GRE (`gre-y`), FOU (`fou-y`), and UDP tunnel support (`udp_tunnel-y`). `bpf_tcp_ca.o` is compiled only when both `CONFIG_BPF_JIT=y` and `CONFIG_BPF_SYSCALL` are enabled.

## State and persistence
The file has no runtime state; it determines the build graph and resulting built-in objects/modules.

## Dependencies and integration points
It consumes symbols from `net/ipv4/Kconfig` and other subsystem Kconfigs such as XFRM, BPF, NETFILTER, PROC_FS, and SYSCTL. It directly wires source files like `af_inet.c`, `arp.c`, `datagram.c`, `ah4.c`, `cipso_ipv4.c`, and `bpf_tcp_ca.c` into the build when relevant.

## Risks and invariants
Core `obj-y` entries must remain complete enough for AF_INET to initialize base protocols. Optional object rules must match Kconfig dependencies; otherwise configs may expose symbols without objects or compile objects without required infrastructure. The extra Makefile gate on `CONFIG_BPF_JIT` is a subtle integration constraint for BPF TCP congestion control.

## Test signals
Build-matrix coverage should exercise minimal IPv4, proc/sysctl, netfilter, IPsec AH/ESP/IPComp, tunnels, all diagnostics, congestion-control modules, NetLabel, XFRM, and BPF JIT/SYSCALL combinations. `make V=1` or generated `.mod` files can confirm expected object inclusion.
