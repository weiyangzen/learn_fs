# sources/distributed-fs/ceph-client/drivers/connector/cn_proc.c

## Purpose
This file implements the process-events connector producer. It lets userspace subscribe over NETLINK_CONNECTOR and receive fork, exec, uid/gid, sid, ptrace, comm, coredump, and exit events from the initial pid/user namespace.

## Important APIs, Types, And Functions
The connector callback ID is `cn_proc_event_id = { CN_IDX_PROC, CN_VAL_PROC }`. Listener count is tracked by `proc_event_num_listeners`. `struct local_event` provides a per-CPU sequence counter protected by `local_lock_t`. `buffer_to_cn_msg()` aligns a stack buffer so the embedded `struct proc_event` is 8-byte aligned. Event emitters include `proc_fork_connector()`, `proc_exec_connector()`, `proc_id_connector()`, `proc_sid_connector()`, `proc_ptrace_connector()`, `proc_comm_connector()`, `proc_coredump_connector()`, and `proc_exit_connector()`. Subscription control is handled by `cn_proc_mcast_ctl()` and acknowledgements by `cn_proc_ack()`.

## Control Flow
Each event emitter first checks whether any listeners exist. It then fills a stack `cn_msg` and `proc_event`, timestamps it, copies relevant task identifiers under RCU where needed, sets message metadata, and calls `send_msg()`. `send_msg()` increments the per-CPU sequence, records CPU number, builds filter data, and broadcasts through `cn_netlink_send_mult()` with a per-socket filter.

Userspace controls subscriptions by sending either a `struct proc_input` or legacy multicast op. `cn_proc_mcast_ctl()` rejects callers outside the initial user and pid namespaces, stores per-socket subscription state in `sk_user_data`, updates the global listener count on LISTEN/IGNORE transitions, and sends an ack with positive errno-style values. `cn_proc_init()` registers the callback with the connector subsystem using `device_initcall`.

## State And Persistence
Persistent state includes global listener count, per-socket `struct proc_input` stored in `sk_user_data`, and per-CPU sequence counters. The state lives as long as connector sockets/callbacks exist. Socket cleanup is coordinated by connector release code in `connector.c`.

## Dependencies And Integration Points
The file depends on scheduler/process hooks calling its exported connector functions, connector core `cn_add_callback()` and `cn_netlink_send_mult()`, `linux/cn_proc.h` ABI structures, RCU task parent/credential access, pid/user namespace checks, and netlink socket user data.

## Risks And Edge Cases
The global listener count is an optimization and can become sensitive to missed LISTEN/IGNORE transitions. Event filtering is per socket and supports `PROC_EVENT_NONZERO_EXIT`. Process events are intentionally limited to init namespaces. Stack buffer alignment depends on `BUILD_BUG_ON(sizeof(struct cn_msg) != 20)`. Ack error values are positive errno numbers by ABI convention rather than normal negative kernel returns.

## Test Signals
Tests should cover subscribe/unsubscribe acks, per-event payload fields, namespace rejection, per-socket filters including nonzero exit, sequence ordering per CPU, listener count transitions, and cleanup of `sk_user_data` when sockets close.
