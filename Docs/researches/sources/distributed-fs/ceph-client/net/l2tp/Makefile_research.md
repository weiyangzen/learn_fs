# sources/distributed-fs/ceph-client/net/l2tp/Makefile

## Purpose
Maps L2TP Kconfig symbols to kernel objects and ensures the core source is compiled with the local include path.

## Important build rules
- `obj-$(CONFIG_L2TP) += l2tp_core.o` builds the core.
- `CFLAGS_l2tp_core.o += -I$(src)` makes local headers such as `trace.h` visible.
- `obj-$(subst y,$(CONFIG_L2TP),$(CONFIG_PPPOL2TP)) += l2tp_ppp.o` forces PPPoL2TP module behavior to follow core L2TP when core is modular.
- Similar `subst` rules build `l2tp_ip.o`, `l2tp_netlink.o`, `l2tp_eth.o`, and `l2tp_debugfs.o`.
- `l2tp_ip6.o` is added only when `CONFIG_IPV6` is non-empty and `CONFIG_L2TP_IP` is enabled.

## Control flow and integration
This is a Kbuild integration file. It ensures optional modules align with core L2TP linkage so optional pieces are not built in a way that cannot link to core support.

## State and persistence behavior
No runtime state is present. The only persistent effect is build graph structure.

## Risks and test signals
The main risk is modularity mismatch across core and optional L2TP pieces. Build matrix tests should cover built-in and module variants for `L2TP`, `PPP`, `L2TP_IP`, `L2TP_V3`, `L2TP_ETH`, `L2TP_DEBUGFS`, and `IPV6`.
