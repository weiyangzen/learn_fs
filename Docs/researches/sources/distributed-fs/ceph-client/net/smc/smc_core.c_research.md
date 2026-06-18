# sources/distributed-fs/ceph-client/net/smc/smc_core.c

## Purpose
`smc_core.c` is the central lifetime and resource manager for Linux SMC link groups, links, connections, buffers, remote RMB tokens, and SMC-R/SMC-D teardown. It bridges connection setup from CLC negotiation into reusable link groups, allocates and maps SMC-R RDMA memory or SMC-D DMBs, exposes link-group state through generic netlink dump helpers, and reacts to RDMA/ISM device shutdown.

## Important APIs, Types, and Functions
Key exports include `smc_conn_create()`, `smc_conn_free()`, `smc_buf_create()`, `smcd_buf_attach()`, `smcr_link_init()`, `smcr_link_clear()`, `smcr_link_down_cond_sched()`, `smc_smcr_terminate_all()`, `smc_smcd_terminate_all()`, `smc_rtoken_add()`, `smc_rtoken_delete()`, and generic netlink dump entry points for system, SMC-R link groups, SMC-R links, and SMC-D link groups. The file owns global `smc_lgr_list`, `lgr_cnt`, and the `lgrs_deleted` wait queue for SMC-R groups. It uses `struct smc_link_group`, `struct smc_link`, `struct smc_buf_desc`, and `struct smc_rtoken` from `smc_core.h`.

## Control Flow
Connection setup starts in `smc_conn_create()`. It selects an SMC-D device list or global SMC-R list, tries to match an existing group with `smcd_lgr_match()` or `smcr_lgr_match()`, registers the connection under `conns_lock`, or creates a new group via `smc_lgr_create()`. New SMC-R groups allocate per-group WR memory, initialize LLC, create the first link with `smcr_link_init()`, and register in `smc_lgr_list`; SMC-D groups take an ISM device reference and are registered on the device's group list. Teardown flows through delayed free work, scheduled terminate work, device-wide termination, or early cleanup paths. SMC-R link loss routes through `smcr_link_down_cond_sched()`, `smc_link_down_work()`, `smc_switch_conns()`, LLC delete-link handling, and finally `smcr_link_clear()`.

## State and Persistence
All state is in-memory kernel state: link groups in lists, connections in an rb-tree keyed by alert token, reusable send/RMB buffer lists per compressed size, rtoken bitmaps, per-link reference counts, and delayed work items. No durable persistence exists. Refcounts (`smc_lgr_hold/put`, `smcr_link_hold/put`), socket holds, delayed work, wait queues, rwsems, spinlocks, and atomics preserve lifetime while link groups are visible to sockets, netlink, RDMA callbacks, and workqueues. Buffer descriptors may be reused after `used` is cleared and memory is zeroed.

## Dependencies and Integration Points
This file depends on RDMA verbs and SMC WR helpers for SMC-R mapping, QP setup, memory registration, and send/receive wakeups; ISM helpers for SMC-D DMB registration and peer shutdown signaling; LLC for link add/delete and rkey negotiation; CDC/close/stat/trace modules for connection state and diagnostics; and generic netlink for state dumps. It is initialized through `smc_core_init()` and cleaned by `smc_core_exit()`, with a reboot notifier that shuts down SMC-R and SMC-D devices before unregistering lower clients.

## Risks
The main risks are concurrency and lifetime bugs: link groups can be removed from public lists while connections, work items, and device callbacks still hold references; LLC and buffer registration paths must not race link deletion; reusable buffers must be fully unmapped, deregistered, zeroed, or freed after registration errors; and alert-token rb-tree updates require correct `conns_lock` coverage. SMC-D peer GID matching has different behavior for emulated devices, so incorrect matching can terminate or reuse the wrong group. Netlink dump paths hold locks while filling skbs, so message-size failures must leave cursor state coherent.

## Test Signals
Useful tests include SMC-R and SMC-D connect/reuse/close cycles, repeated connection churn to exercise delayed free work, link failover with two active RoCE paths, device removal during traffic, DMB no-copy attach/detach, VLAN negotiation, memory-pressure buffer downgrade, rtoken add/delete under parallel connection creation, generic netlink dumps for link groups and links, and reboot/module-unload teardown with no leaked references or hung waits.
