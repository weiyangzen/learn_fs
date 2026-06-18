# sources/distributed-fs/ceph-client/net/tipc/Makefile

## Purpose
This Makefile defines the object composition of the TIPC protocol module or built-in object.

## Important APIs, Types, And Functions
`obj-$(CONFIG_TIPC) := tipc.o` builds the aggregate protocol object. `tipc-y` lists the core objects: address, broadcast, bearer, core, link, discovery, message, name distribution, subscription, monitor, name table, netlink, node, socket, Ethernet media, topology server, group, and trace support. Conditional entries add UDP media, InfiniBand media, sysctl, and crypto. `TIPC_DIAG` builds `tipc_diag.o` from `diag.o`.

## Control Flow
Kbuild links conditional objects into the aggregate based on configuration symbols. `CFLAGS_trace.o += -I$(src)` adds source include path for trace generation.

## State And Persistence
No runtime state exists. The persistent effect is the compiled object graph for each kernel configuration.

## Dependencies And Integration Points
The Makefile integrates TIPC with Kbuild, optional media implementations, sysctl, crypto, and diagnostic modules.

## Risks And Test Signals
Risks include missing conditional object coverage and trace include path problems. Test signals are matrix builds for `TIPC=y`, `TIPC=m`, UDP/IB/crypto/sysctl combinations, and `TIPC_DIAG` module builds.
