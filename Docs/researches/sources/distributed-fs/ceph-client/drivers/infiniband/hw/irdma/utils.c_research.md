# sources/distributed-fs/ceph-client/drivers/infiniband/hw/irdma/utils.c

## Purpose

`utils.c` is the IRDMA driver support layer behind the uverbs-facing code. It manages ARP/cache state from Linux networking notifications, wraps hardware register access, owns much of the Control Queue Pair (CQP) request lifecycle, issues common CQP operations for QP/CQ/SRQ/AH/stats/work-scheduler resources, handles terminate and exception-queue helpers, manages PBLE backing memory, and synthesizes flush completions when QPs are torn down.

## Important APIs, Types, and Functions

- `irdma_arp_table`, `irdma_add_arp`, `irdma_inetaddr_event`, `irdma_inet6addr_event`, `irdma_net_event`, `irdma_netdevice_event`, and `irdma_add_ip` keep the driver's software and hardware ARP/MAC/IP view synchronized with netdev, VLAN, IPv4, IPv6, and neighbor state.
- `wr32`, `rd32`, and `rd64` are direct MMIO access helpers over `struct irdma_hw`.
- `irdma_alloc_and_get_cqp_request`, `irdma_put_cqp_request`, `irdma_cleanup_pending_cqp_op`, `irdma_wait_event`, `irdma_cqp_crit_err`, and `irdma_handle_cqp_op` are the core CQP request allocator, waiter, error classifier, cleanup path, and dispatcher.
- QP/CQ/SRQ CQP wrappers include `irdma_cqp_qp_create_cmd`, `irdma_cqp_qp_destroy_cmd`, `irdma_cqp_cq_create_cmd`, `irdma_cq_wq_destroy`, `irdma_srq_wq_destroy`, `irdma_hw_modify_qp`, `irdma_cqp_qp_suspend_resume`, and `irdma_modify_qp_to_err`.
- Termination helpers `irdma_terminate_start_timer`, `irdma_terminate_done`, and `irdma_terminate_del_timer` coordinate iWARP terminate completion, timeout fallback, CM disconnect, hash removal, and QP references.
- Exception and PUDA helpers include `irdma_ieq_check_mpacrc`, `irdma_ieq_get_qp`, `irdma_send_ieq_ack`, `irdma_puda_ieq_get_ah_info`, `irdma_puda_get_tcpip_info`, `irdma_puda_create_ah`, and `irdma_puda_free_ah`.
- Stats helpers include `irdma_hw_stats_start_timer`, `irdma_hw_stats_stop_timer`, `irdma_cqp_gather_stats_gen1`, `irdma_cqp_gather_stats_cmd`, and `irdma_cqp_stats_inst_cmd`.
- PBLE helpers include `irdma_prm_add_pble_mem`, `irdma_prm_get_pbles`, `irdma_prm_return_pbles`, `irdma_map_vm_page_list`, `irdma_pble_get_paged_mem`, and `irdma_pble_free_paged_mem`.
- Completion helpers `irdma_remove_cmpls_list`, `irdma_generated_cmpls`, and `irdma_generate_flush_completions` support software-generated CQEs for flushed WQEs.

## Control Flow

Network event flow starts from kernel notifiers. Address add/change paths resolve the real VLAN parent, locate the registered IRDMA `ib_device`, update the hardware ARP cache via `irdma_manage_arp_cache` or `irdma_add_arp`, notify CM address state through `irdma_if_notify`, and dispatch `IB_EVENT_GID_CHANGE`. Neighbor updates add or delete ARP entries based on `NUD_VALID`. Initial device bring-up calls `irdma_add_ip`, which scans all relevant up netdevices under RCU and seeds IPv4 and IPv6 addresses.

CQP operations follow a common pattern. A caller gets a `struct irdma_cqp_request` from the preallocated available list or from atomic dynamic allocation, fills `cqp_request->info`, sets a scratch pointer back to the request, and calls `irdma_handle_cqp_op`. The dispatcher posts through `irdma_process_cqp_cmd`; synchronous callers then call `irdma_wait_event`, which services the CCQ, waits on the per-request waitqueue, switches to the deferred timeout threshold when a pending completion is observed, and requests a device reset on command progress timeout. Completion and reset cleanup free pending requests, wake waiters with error state, and drain both hardware ring scratch entries and software command list nodes.

Resource operations are thin command builders over that CQP substrate. QP/CQ/SRQ create and destroy functions fill operation-specific `cqp_info->in.u.*` fields. `irdma_hw_modify_qp` can wait synchronously or install a completion callback that decrements `iwqp->hw_mod_qp_pend`; on iWARP bad-close style failures it may generate an async event, send reset, or force an ERROR transition. AH, multicast-related AH, stats, CEQ/AEQ, work-scheduler, and STATS instance commands all reuse the same request mechanics.

Exception-queue flow parses received TCP/IP headers from PUDA buffers differently for generation 1 and newer hardware, finds the owning CM node/QP by the packet four-tuple, validates MPA CRCs, builds loopback AH info for partial FPDU handling, and sends duplicate/out-of-order ACKs through the CM TCP context. Terminate flow adds a temporary QP reference while a one-second timer is armed; successful or timed-out termination funnels through `irdma_terminate_done`, which marks `IRDMA_TERM_DONE`, transitions to ERROR once, and disconnects CM.

Flush completion generation is deferred until the hardware CQ is empty. `irdma_generate_flush_completions` walks SQ and RQ rings under CQ and QP locks, creates `struct irdma_cmpl_gen` entries with flushed status and original WR IDs, advances software ring tails, skips SQ NOPs, and invokes CQ completion handlers when new generated CQEs are queued. If the real CQ still has entries, it reschedules the delayed flush work.

## State and Persistence

All state is runtime kernel state. The file mutates ARP table entries and bitmaps under `rf->arp_lock`, CQP request lists under `cqp->req_lock`, resource bitmaps for QPs/CQs/SRQs/AHs/MCGs/work-scheduler nodes, QP/CQ reference counts and completion objects, QP terminate timers, delayed flush work, hardware stats timers, PBLE manager bitmaps, and generated-completion lists. Persistent external effects are limited to hardware MMIO/CQP state, DMA mappings, and RDMA core events while the driver is loaded.

## Dependencies and Integration Points

The file depends on Linux netdevice, inetaddr, inet6addr, neighbor, VLAN, RCU, timer, workqueue, DMA, vmalloc, CRC32C, and RDMA core APIs. Internally it integrates with `main.h` structures, the low-level `irdma_sc_*` hardware library, CM helpers, work-scheduler helpers, PBLE resource management, PUDA ILQ/IEQ paths, `verbs.c` object teardown and polling paths, and `virtchnl.c` for generation 3 GSI/vport cleanup.

## Risks

The highest risks are concurrency and lifetime defects. CQP requests are referenced by hardware scratch fields, software lists, waitqueues, callbacks, and reset cleanup; a missed refcount transition can leak a request or wake freed memory. QP/CQ table entries are sampled by interrupts, so refcount completion and `WRITE_ONCE`/locking discipline matters. Generated flush completions mutate work-queue rings outside normal hardware completion flow and must not race post-send/post-recv. Network notifier paths use RCU and `ib_device_get_by_netdev`; mistakes can leave stale ARP entries or dispatch GID changes for the wrong VLAN parent. PBLE page mapping error unwinds must unmap only successfully mapped pages. Timeout-driven reset requests are intentionally broad and can turn localized CQP stalls into device reset events.

## Test Signals

Useful signals include ARP add/update/delete through IPv4, IPv6, VLAN, and neighbor changes; CQP success, noncritical error, critical error, deferred completion, timeout, and reset paths; QP modify to RTS, SQD, ERROR, terminate timeout, and bad-close paths; CQ/QP/SRQ create and destroy leak checks; generated flush completions after outstanding SQ/RQ WQEs; stats timer and on-demand stats reads on gen1 and gen2+ hardware; PBLE allocation/free fragmentation tests; PUDA IEQ parsing for gen1 and newer packet layouts; and fault injection for DMA allocation, CQP request allocation, and `dma_map_page` failures.
