# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_sp.h

## Purpose

`qed_sp.h` declares the QED slow-path service processor interface used by the Ethernet, storage, RDMA, and SR-IOV portions of the driver to submit firmware ramrods, receive event-ring completions, and manage slow-path queues. It is the shared contract for SPQ entries, event queues, consolidation queues, request initialization, and PF lifecycle ramrods.

## Important APIs, Types, and Data Structures

- `enum spq_mode` defines completion ownership: `QED_SPQ_MODE_BLOCK` uses caller-supplied polling memory, `QED_SPQ_MODE_CB` uses callbacks, and `QED_SPQ_MODE_EBLOCK` blocks inside the QED SPQ layer until completion.
- `struct qed_spq_comp_cb`, `union qed_spq_req_comp`, and `struct qed_spq_comp_done` model callback completion, external done-address completion, and internal EBLOCK completion state.
- `union ramrod_data` is the central payload union for slow-path firmware commands. It covers common PF start/update/stop, Ethernet queue and vport operations, GFT/filter updates, RDMA/RoCE/iWARP, FCoE, iSCSI, NVMf/TCP, and VF start/stop ramrods.
- `struct qed_spq_entry` wraps a firmware `slow_path_element`, the ramrod data, queue linkage, priority, completion mode/callback state, and the `post_ent` back-reference used when an unlimited EBLOCK entry is copied into a real ring entry.
- `struct qed_spq` owns the SPQ lock, the pending/completion/free/unlimited lists, DMA-backed entry array, `qed_chain`, out-of-order completion bitmap, counters, SPQ CID, doorbell data, and per-protocol async-completion callbacks.
- `struct qed_eq` wraps the firmware event ring chain plus interrupt-status-block index and firmware consumer pointer. `struct qed_consq` wraps the consolidation queue chain.
- Public functions include `qed_spq_alloc/setup/free`, `qed_spq_get_entry/post/return_entry/completion/pend_post/get_cid`, `qed_eq_alloc/setup/free/prod_update/completion`, `qed_consq_alloc/setup/free`, `qed_spq_register_async_cb`, and common PF ramrods such as `qed_sp_pf_start`, `qed_sp_pf_update`, `qed_sp_pf_update_tunn_cfg`, `qed_sp_pf_stop`, and `qed_sp_heartbeat_ramrod`.

## Control Flow

The header describes a standard slow-path command lifecycle. Callers allocate or obtain an SPQ entry with `qed_spq_get_entry`, initialize it through `qed_sp_init_request`, fill the specific member of `union ramrod_data`, and submit it with `qed_spq_post`. Firmware completions arrive on the EQ or selected CQE paths and are routed to `qed_spq_completion`, which matches the `echo` field against `completion_pending` entries and invokes the configured callback. Async firmware events are dispatched through the `async_comp_cb[MAX_PROTOCOL_TYPE]` table instead of the SPQ completion list.

PF lifecycle control is layered over the same primitive. PF start fills EQ and ConsQ addresses into a `pf_start_ramrod_data`, PF update emits common update ramrods for DCBX/UFP/tunnel/STAG changes, PF stop and heartbeat use EBLOCK mode to wait for firmware acknowledgement.

## State and Persistence Behavior

All state is in kernel memory and firmware-visible DMA memory. The SPQ keeps persistent runtime lists and a DMA array of `qed_spq_entry` objects whose `ramrod` members are referenced by firmware through `elem.data_ptr`. The EQ and ConsQ persist as `qed_chain` objects while the hardware function is active. No disk persistence exists. State is reset during setup and freed during device teardown.

The header makes completion ownership explicit: CB and BLOCK entries may be returned by completion handling, while EBLOCK entries are retained until the posting caller finishes waiting. This distinction is critical because EBLOCK callers continue to dereference the entry after firmware completion.

## Dependencies and Integration Points

`qed_sp.h` depends on Linux list, spinlock, slab, and QED chain helpers, and on firmware HSI definitions from `qed_hsi.h`. It integrates with:

- `qed_spq.c` for queue allocation, posting, completion matching, EQ dispatch, and ConsQ management.
- `qed_sp_commands.c` for common PF ramrod construction.
- Ethernet, RDMA, FCoE, iSCSI, NVMf/TCP, and SR-IOV modules through the shared `union ramrod_data`.
- Doorbell, context, interrupt, and firmware event mechanisms through the SPQ/EQ declarations.

## Risks and Edge Cases

- `union ramrod_data` is a wide ABI surface tied to firmware HSI structs. Adding or changing ramrod payloads must preserve alignment and data-pointer expectations.
- Misusing completion modes can cause use-after-free or leaks. EBLOCK entries must not be returned by completion code, while non-EBLOCK entries must not be retained by callers after post.
- `SPQ_RING_SIZE` derives from `CORE_SPQE_PAGE_SIZE_BYTES / sizeof(struct slow_path_element)`, so firmware page-size and structure-size changes can affect bitmap and chain assumptions.
- Async callback registration is per protocol with no multiplexing; two subsystems registering the same protocol would overwrite each other.
- Because the SPQ is shared by many upper-layer modules, a hung ramrod, missing completion, or bad echo affects PF lifecycle and VF mailbox handling.

## Test Signals

Useful validation signals are successful PF start/stop/heartbeat ramrods, clean SPQ allocation/setup/free under probe/remove, event-ring completions matching posted echo values, no leaked SPQ entries after CB and EBLOCK operations, async callback dispatch for SR-IOV common events, and stress tests that post more ramrods than the ring capacity to exercise `unlimited_pending`.
