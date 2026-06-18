# sources/distributed-fs/ceph-client/net/ipv6/ila/ila_main.c

## Purpose
Defines ILA module initialization, generic-netlink family operations, netlink attribute policy, and per-network namespace lifecycle. It wires the xlat mapping subsystem and lwtunnel support into a single module.

## Important APIs, Types, and Functions
Defines `ila_nl_policy`, `ila_nl_ops`, exported `ila_net_id`, and exported `struct genl_family ila_nl_family`. Netlink commands map to `ila_xlat_nl_cmd_add_mapping()`, delete, flush, get, and dump callbacks. Namespace functions are `ila_init_net()`, `ila_pre_exit_net()`, and `ila_exit_net()`. Module lifecycle is `ila_init()`/`ila_fini()`.

## Control Flow
Module init registers pernet device state first, then the generic-netlink family, then lwtunnel encap ops. Failure unwinds in reverse order. Netlink add/delete/flush require admin permission; get supports dump start/dump/done callbacks. Per-net init initializes xlat state; pre-exit and exit tear it down. Module exit unregisters lwtunnel ops, generic-netlink family, and pernet device state.

## State and Persistence
Per-net state size is `sizeof(struct ila_net)` and is referenced through `ila_net_id`. Generic-netlink family metadata is `__ro_after_init`. Xlat mappings are runtime netlink state owned by `ila_xlat.c`; this file manages lifecycle only.

## Dependencies and Integration Points
Depends on generic netlink, network namespace generic storage, ILA xlat implementation, ILA lwtunnel registration, and UAPI command/attribute constants. It is the module-level integration point for user-space ILA management.

## Risks and Test Signals
Risks include registration unwind leaks, net namespace teardown ordering, relaxed genl validation compatibility, admin permission enforcement, and lwt/xlat lifecycle ordering. Test signals include module load/unload, namespace creation/destruction, genl add/del/get/dump/flush commands, permission checks, and forced failure injection at each registration step.
