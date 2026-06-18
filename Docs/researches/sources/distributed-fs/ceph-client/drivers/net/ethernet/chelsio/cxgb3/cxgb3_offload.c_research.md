# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb3/cxgb3_offload.c

## Purpose

`cxgb3_offload.c` implements the Chelsio T3 offload service layer used by upper-layer protocol clients such as iSCSI and RDMA. It manages offload client registration, active offload device registration, TID/STID/ATID tables, CPL opcode dispatch, neighbor/redirect notifications, RDMA/iSCSI control queries, and activation/deactivation of per-adapter offload state. It is the main software bridge between the generic Ethernet adapter in `cxgb3_main.c`, the firmware work-request protocol, the L2 table in `l2t.c`, and external protocol clients.

## Important APIs, types, and functions

- Client registry: `cxgb3_register_client()`, `cxgb3_unregister_client()`, `cxgb3_add_clients()`, `cxgb3_remove_clients()`, and `cxgb3_event_notify()` maintain `client_list` and call client `add`, `remove`, and `event_handler` callbacks under `cxgb3_db_lock`.
- Device registry: `register_tdev()`, `unregister_tdev()`, `cxgb3_adapter_ofld()`, and `cxgb3_adapter_unofld()` maintain `ofld_dev_list`, initialize `struct t3cdev` callbacks, set dummy receive/neigh handlers before activation, and assign T3A/T3B/T3C type from adapter revision.
- Activation: `cxgb3_offload_activate()` allocates `struct t3c_data`, queries `tdev->ctl` for limits/ranges/MTUs/L2T capacity, allocates `l2t_data`, initializes TID tables, installs RCU L2 data, switches `dev->recv` to `process_rx`, sets `dev->neigh_update`, registers the netevent notifier once, and adds the adapter to `adapter_list`.
- Deactivation: `cxgb3_offload_deactivate()` removes the adapter from the global adapter list, unregisters the netevent notifier when no adapters remain, frees TID maps, clears `T3C_DATA`, removes RCU L2 data with `call_rcu()`, frees reserve skb and `struct t3c_data`.
- Control dispatch: `cxgb_offload_ctl()` handles firmware work-request sizes, TID/STID ranges, L2T capacity, MTUs, MAC-to-interface lookup, DDP params, port list, iSCSI params, RDMA params/context ops/memory/MIB, RX page info, iSCSI IPv4 address, and embedded firmware/TP versions.
- TID services: `cxgb3_alloc_atid()`, `cxgb3_free_atid()`, `cxgb3_insert_tid()`, `cxgb3_remove_tid()`, `cxgb3_queue_tid_release()`, and `t3_process_tid_release_list()` allocate active-open IDs, install hardware TID contexts, and send deferred `CPL_TID_RELEASE` work requests.
- CPL dispatch: `t3_register_cpl_handler()`, `process_rx()`, `do_stid_rpl()`, `do_hwtid_rpl()`, `do_cr()`, `do_act_open_rpl()`, `do_act_establish()`, `do_abort_req_rss()`, `do_term()`, `do_trace()`, and simple write-reply handlers map firmware CPL opcodes to per-client handlers or built-in replies.
- Neighbor integration: `nb_callback()`, `cxgb_neigh_update()`, `cxgb_redirect()`, `set_l2t_ix()`, and `is_offloading()` map netevent neighbor/redirect notifications to L2T updates and optional client redirect callbacks.

## Control flow

At module initialization, `cxgb3_offload_init()` fills every CPL opcode slot with `do_bad_cpl()` and registers built-in dispatch handlers for SMT/L2T/RTE replies, passive/active open, established/close/abort/data/RDMA/iSCSI/trace events. During PCI probe, `cxgb3_adapter_ofld()` registers an inactive `t3cdev` with dummy receive and neighbor callbacks. During `offload_open()` in `cxgb3_main.c`, `cxgb3_offload_activate()` builds offload runtime state and then `cxgb3_add_clients()` notifies all registered clients.

Receive flow enters `process_rx()` through `t3cdev.recv`. The SGE path has encoded the CPL opcode in `skb->csum` and the hardware TID in `skb->priority`; `process_rx()` indexes `cpl_handlers`, invokes the selected handler, logs unknown TIDs when validation is enabled, and frees the skb if the handler returns `CPL_RET_BUF_DONE`. Most CPL handlers look up a `struct t3c_tid_entry` in the active, server, or hardware TID tables and then call the corresponding client handler with the stored context. If no client/context/handler exists, the packet is logged as clientless and treated as a bad message.

Transmit/control flow uses `cxgb3_ofld_send()`, which disables bottom halves around `dev->send()`. TID release is usually sent immediately from `cxgb3_remove_tid()` for non-T3A adapters; if atomic allocation fails, the TID entry is chained through `ctx` into `tid_release_list` and `t3_process_tid_release_list()` later emits `CPL_TID_RELEASE` work requests using a reserve skb if needed.

Neighbor flow is driven by the kernel netevent notifier. `NETEVENT_NEIGH_UPDATE` calls `t3_l2t_update()` for devices belonging to offloading adapters. `NETEVENT_REDIRECT` allocates a new L2T entry for the redirected destination, walks all active hardware TIDs, asks each client `redirect()` callback whether to update the TCB, and sends `CPL_SET_TCB_FIELD` with the new L2T index when requested.

## State and persistence behavior

Global volatile state includes `client_list`, `ofld_dev_list`, `adapter_list`, `cxgb3_db_lock`, and `adapter_list_lock`. Per-active-offload state is stored in `struct t3c_data` via `T3C_DATA(tdev)`, including MTU table pointer, work-request limits, `struct tid_info`, TID-release work item/list/lock, reserve skb, and `l2opt` RCU pointer to `struct l2t_data`. TID maps are allocated as one `kvzalloc()` block partitioned into hardware TID, server TID, and active-open TID arrays with free lists for STIDs/ATIDs. No state persists across driver unload or offload deactivation; hardware-visible TID/L2T/TCB state is programmed through firmware work requests and discarded/reset through adapter lifecycle.

Concurrency uses a mutex for client/device callbacks, rwlock for adapter lookup from netdevice, per-TID free-list spinlocks, `tid_release_lock`, RCU for L2T pointer replacement, atomics for active hardware TID count, and bottom-half disabling around offload send paths.

## Dependencies and integration points

This file depends on `common.h`/`t3cdev.h` adapter definitions, `regs.h` register constants, `cxgb3_ctl_defs.h` control request structs, `cxgb3_defs.h`, `l2t.h`, `t3_cpl.h` CPL layouts/opcodes, and `firmware_exports.h` work-request opcodes and queue/TID constants. It integrates with Linux neighbour and redirect netevents, VLAN/bond upper-device lookup, sk_buff control blocks, workqueues, vmalloc-backed allocation, RCU cleanup, and exported symbols consumed by offload protocol modules.

## Risks and edge cases

- Client callbacks are invoked while `cxgb3_db_lock` is held; callbacks must not re-enter registration paths or block indefinitely.
- CPL opcode extraction depends on SGE-specific use of `skb->priority` and `skb->csum`; changes in receive plumbing must preserve this contract.
- `process_rx()` trusts `cpl_handlers[opcode]`; opcode validity depends on `NUM_CPL_CMDS` and encoded values from SGE/firmware.
- `cxgb_redirect()` scans every hardware TID under redirect events, which can be expensive for large TCAM sizes.
- `set_l2t_ix()` uses `GFP_ATOMIC`; allocation failure logs and drops the TCB update, leaving clients with software redirect state but stale hardware L2T index.
- `cxgb3_offload_deactivate()` assumes offload clients have been removed and release work flushed by the caller. Lifetime bugs could leave client contexts referenced in TID tables during `free_tid_maps()`.
- `cxgb3_remove_tid()` uses `cmpxchg()` only for T3A; other revisions clear `ctx` after sending or queueing release, so ordering with delayed client CPL processing is part of the documented race model.
- `get_iff_from_mac()` handles VLAN and bond master lookup under RCU, but returns a `net_device *` without taking a reference; callers must respect expected transient lifetime.

## Test signals

Validation should cover offload activate/deactivate loops, client register/unregister before and after activation, CPL dispatch for every built-in opcode class, clientless/bad CPL logging, ATID exhaustion and free-list reuse, TID removal under GFP_ATOMIC allocation failure, deferred release work flushing, iSCSI/RDMA control requests when offload is stopped vs running, netevent neighbor update and redirect behavior, RCU teardown under concurrent lookup, and `cxgb3_ofld_send()` behavior from process and softirq contexts.
