# sources/distributed-fs/ceph-client/net/tipc/core.c

## Purpose
This file is the TIPC module entry point and per-network-namespace lifecycle manager.

## Important APIs, Types, And Functions
It defines global configurable state `tipc_net_id` and `sysctl_tipc_rmem`. Main functions are `tipc_init_net()`, `tipc_exit_net()`, `tipc_pernet_pre_exit()`, module init `tipc_init()`, and module exit `tipc_exit()`. It registers pernet operations for `struct tipc_net`, topology server pernet operations, and pre-exit cleanup.

## Control Flow
Per-net initialization sets default network id, node/trial address state, capabilities, work item, node ID strings, monitor threshold, random salt, node list, lock, optional crypto, socket rhashtable, name table, broadcast link, and loopback packet hook. Failure unwinds in reverse order. Module initialization registers sysctl, pernet device state, socket family, topology server state, pre-exit hook, bearer notifier, netlink, and compatibility netlink. Exit reverses these registrations and stops per-net resources.

## State And Persistence
TIPC global tunables live in memory. Each namespace receives a `struct tipc_net` allocated by pernet generic storage. Exit cancels finalize work, stops broadcast/name/socket/crypto state, detaches loopback, stops network state, and waits for scheduled work queue count to drain.

## Dependencies And Integration Points
Dependencies include TIPC name table, subscription, bearer, net, socket, broadcast, node, optional crypto, module infrastructure, sysctl, pernet APIs, netlink, and topology server components.

## Risks And Test Signals
Risks include partial initialization unwind, work item races during namespace teardown, crypto conditional cleanup, and module init ordering. Test signals include module load/unload, net namespace create/destroy loops, fault injection in each init stage, TIPC socket creation, bearer enable after module init, and lock/workqueue leak checks during exit.
