# Research Report: subset-b-004607

Grouped research for QLogic QED service-processor, SPQ, and SR-IOV PF/VF control files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_sp.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_sp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_sp_commands.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_sp_commands.c

## Purpose

`qed_sp_commands.c` implements common slow-path ramrod construction for PF initialization, PF updates, PF shutdown, heartbeat, UFP/STAG updates, and tunnel configuration. It converts driver state into firmware HSI payloads and submits those payloads through the SPQ API declared in `qed_sp.h`.

## Important APIs and Functions

- `qed_sp_destroy_request()` returns a request to the correct owner after initialization failures. Entries taken from `free_pool` go back to the pool, while entries allocated for `unlimited_pending` are freed.
- `qed_sp_init_request()` obtains an SPQ entry, fills the opaque FID/CID header, command ID, protocol ID, completion mode, and completion callback cookie, then clears `ramrod` payload storage.
- Tunnel helper functions translate driver tunnel configuration into firmware format: `qed_tunn_clss_to_fw_clss()`, `qed_set_pf_update_tunn_mode()`, `qed_set_tunn_cls_info()`, `qed_set_tunn_ports()`, `qed_set_ramrod_tunnel_param()`, `qed_tunn_set_pf_update_params()`, `qed_set_hw_tunn_mode()`, `qed_set_hw_tunn_mode_port()`, and `qed_tunn_set_pf_start_params()`.
- `qed_sp_pf_start()` builds and posts `COMMON_RAMROD_PF_START`, configuring event ring, consolidation queue, multi-function outer tag behavior, personality, tunnel config, SR-IOV base VF information, and fast-path HSI version.
- `qed_sp_pf_update()` emits `COMMON_RAMROD_PF_UPDATE` carrying DCBX result updates.
- `qed_sp_pf_update_ufp()` and `qed_sp_pf_update_stag()` update UFP priority behavior and outer-tag/STAG data.
- `qed_sp_pf_update_tunn_cfg()` updates PF tunnel classification and UDP port state. VF devices are routed to `qed_vf_pf_tunnel_param_update()` instead of sending a PF ramrod.
- `qed_sp_pf_stop()` and `qed_sp_heartbeat_ramrod()` send EBLOCK common ramrods and wait for firmware completion through SPQ.

## Control Flow

Most exported functions follow the same flow: initialize `struct qed_sp_init_data`, call `qed_sp_init_request()` with a common command and `PROTOCOLID_COMMON`, populate the command-specific member of `p_ent->ramrod`, and call `qed_spq_post()`. PF start uses EBLOCK mode, updates the EQ producer first, writes EQ and ConsQ PBL addresses into the ramrod, selects firmware personality from `p_hwfn->hw_info.personality`, and only after a successful SPQ post applies tunnel mode/port changes to hardware registers.

Tunnel updates are staged in `p_hwfn->cdev->tunnel`. The update path first copies requested mode/class/port fields into the cached driver tunnel state according to update flags, encodes that state into `pf_update_tunnel_config`, posts the PF update ramrod, and then writes hardware tunnel mode/port registers through `qed_set_*` helpers.

## State and Persistence Behavior

This file mutates volatile driver state in `p_hwfn->cdev->tunnel`, reads multi-function flags from `cdev->mf_bits`, reads `hw_info` and `ufp_info`, and sends DMA-backed SPQ payloads to firmware. It does not own long-lived allocations; lifecycle and DMA persistence are owned by SPQ, EQ, and ConsQ code.

The tunnel cache is persistent for the lifetime of the device and is reused across PF start, PF update, and VF tunnel-update responses. PF start also uses `cdev->p_iov_info` to advertise SR-IOV base VF ID and total VF count to firmware when SR-IOV capability exists.

## Dependencies and Integration Points

The file integrates with `qed_spq.c` via `qed_spq_get_entry`, `qed_spq_post`, `qed_spq_return_entry`, and `qed_spq_get_cid`; with interrupt code for EQ status-block IDs; with chain helpers for EQ/ConsQ PBL addresses; with DCBX for PF update payloads; with tunnel hardware helpers in `qed_hw`; and with SR-IOV/VF code for PF start VF counts and VF tunnel parameter updates.

It includes `qed_sriov.h` to use `IS_VF()` and `cdev->p_iov_info`, making PF common commands aware of both PF and VF driver modes.

## Risks and Edge Cases

- `qed_sp_init_request()` returns `-ENOMEM` for a NULL `pp_ent`, although the actual issue is invalid input. Callers likely treat any negative return as fatal, but diagnostics may be misleading.
- Completion-mode setup is strict. `QED_SPQ_MODE_BLOCK` requires caller-provided completion data; missing data destroys the request and returns `-EINVAL`.
- Tunnel state is updated before posting PF update ramrods. If the ramrod fails, the cached `cdev->tunnel` state may already reflect the requested configuration, while hardware may not.
- PF start writes hardware tunnel registers after posting the ramrod regardless of the return path reaching that line; the code returns `rc`, but hardware writes still happen when `p_tunn` is non-NULL even if the ramrod failed.
- Personality selection defaults unknown personalities to Ethernet after logging. That can keep initialization moving but may mask unsupported configuration.
- SR-IOV fields in PF start are populated only if `p_iov_info` exists; mismatches between PCI SR-IOV capability probing and PF start timing can affect firmware VF exposure.

## Test Signals

Good signals include PF start completing in EBLOCK mode with correct EQ/ConsQ PBL programming, PF update calls after DCBX changes, UFP/STAG changes updating firmware fields, tunnel update tests for VXLAN/Geneve/GRE modes and port updates, VF-mode tunnel update routing through VF-PF messaging, and heartbeat failure injection to confirm SPQ stuck-ramrod handling surfaces errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_sp_commands.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_spq.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_spq.c

## Purpose

`qed_spq.c` implements the slow-path queue, event queue, and consolidation queue runtime for QED hardware functions. It allocates DMA chains, initializes firmware context and doorbells, posts slow-path elements, waits for blocking completions, dispatches async events, handles out-of-order completions, and recycles SPQ entries.

## Important APIs and Functions

- Blocking completion: `qed_spq_blocking_cb()`, `__qed_spq_block()`, and `qed_spq_block()` implement EBLOCK/BLOCK waiting. The wait path does a quick udelay poll, then msleep polling, then asks MCP to drain, retries, and finally reports `QED_HW_ERR_RAMROD_FAIL` if the ramrod remains stuck.
- Entry preparation and hardware posting: `qed_spq_fill_entry()` installs the blocking callback when needed; `qed_spq_hw_initialize()` programs the SPQ CID context; `qed_spq_hw_post()` writes the SPQE to the chain and rings the doorbell with memory barriers.
- Async events: `qed_async_event_completion()`, `qed_spq_register_async_cb()`, and `qed_spq_unregister_async_cb()` dispatch firmware async EQEs by protocol.
- EQ operations: `qed_eq_alloc()`, `qed_eq_setup()`, `qed_eq_free()`, `qed_eq_prod_update()`, and `qed_eq_completion()` manage event-ring memory and completion draining.
- CQE completion: `qed_eth_cqe_completion()` routes Ethernet slow-path CQEs to SPQ completion for PFs.
- SPQ lifecycle: `qed_spq_alloc()`, `qed_spq_setup()`, and `qed_spq_free()` allocate chains, DMA-backed entries, doorbell recovery records, and CID context.
- Entry and posting flow: `qed_spq_get_entry()`, `qed_spq_return_entry()`, `qed_spq_add_entry()`, `qed_spq_pend_post()`, `qed_spq_post()`, and `qed_spq_completion()` own list movement and completion callbacks.
- ConsQ lifecycle: `qed_consq_alloc()`, `qed_consq_setup()`, and `qed_consq_free()`.

## Control Flow

During setup, `qed_spq_alloc()` allocates the SPQ object, a single-mode chain of `slow_path_element` entries, and a coherent DMA array of `struct qed_spq_entry`. `qed_spq_setup()` initializes lists and lock, assigns each entry a DMA data pointer to its embedded `ramrod`, acquires a core CID, initializes the firmware context, resets the chain, builds doorbell data, and registers the doorbell for recovery.

Posting starts when a caller obtains an entry. If the free pool is empty, `qed_spq_get_entry()` allocates an entry dynamically and tags it for `unlimited_pending`. `qed_spq_post()` fills callbacks, adds the entry to pending, posts as many pending entries as the ring has capacity for, and, for EBLOCK, waits until completion before returning the entry. `qed_spq_post_list()` moves posted entries to `completion_pending`, writes each SPQE into the chain, and rings the hardware doorbell.

Completions arrive through `qed_eq_completion()` or the Ethernet CQE completion path. EQ completion snapshots the firmware consumer index, consumes each event-ring entry, dispatches async events or SPQ completions, recycles consumed EQ elements, updates the EQ producer, and attempts to post pending SPQ work. `qed_spq_completion()` finds the matching entry by `echo`, updates the out-of-order completion bitmap and chain consumer, invokes the callback outside the lock, and returns non-EBLOCK entries to the free pool.

## State and Persistence Behavior

The module owns transient but long-lived kernel/firmware state: SPQ lists, DMA entry memory, SPQ and EQ chains, completion bitmap, doorbell recovery metadata, and counters. It uses `spin_lock_bh()` to protect SPQ lists and counters. Memory ordering matters in two places: blocking completion uses release/acquire around `comp_done->done`, and hardware posting uses write memory barriers before and after the doorbell.

Recovery mode is treated specially. If `cdev->recov_in_prog` is set, `qed_spq_post()` skips hardware posting and returns success, optionally setting RDMA firmware return codes to success so upper layers can unwind without normal ramrod completion.

## Dependencies and Integration Points

`qed_spq.c` depends on QED chain, context, interrupt, hardware register, MCP, doorbell recovery, RDMA, iSCSI, OOO, and SR-IOV headers. It integrates with:

- Firmware context allocation through `qed_cxt_acquire_cid()` and `qed_cxt_get_cid_info()`.
- Interrupt registration through `qed_int_register_cb()`.
- Doorbell registers through `DOORBELL()`, `qed_db_addr()`, and doorbell recovery registration.
- MCP drain and hardware-error notification for stuck ramrods.
- SR-IOV async events by allowing `qed_sriov_eqe_event()` to register as the common protocol callback.
- Ethernet queue completion through `qed_eth_cqe_completion()`.

## Risks and Edge Cases

- EBLOCK entries from `unlimited_pending` have two objects: the original dynamically allocated entry and a posted pool entry. The `post_ent` ownership path is subtle and must remain consistent to avoid leaks or double returns.
- `qed_spq_comp_bmap_update()` handles out-of-order completions using `echo % SPQ_RING_SIZE`. Any change to echo generation or ring sizing risks returning produced elements too early.
- `qed_spq_post()` returns success immediately in recovery mode without freeing the entry through normal completion flow. Callers rely on recovery semantics and request ownership must be reviewed when adding new callers.
- The doorbell path depends on correct barriers. Removing or weakening `wmb()` can let firmware observe a producer update before the SPQE content is visible.
- `qed_eq_completion()` returns a single `rc` while continuing through events; one bad async or SPQ completion can make the whole drain report failure.
- `qed_spq_get_entry()` can allocate with `GFP_ATOMIC` under pressure. Heavy slow-path bursts can hit allocation failures if the ring is full and no free entries are available.
- Blocking waits can last several seconds before MCP drain and error notification. Tests that inject missing completions should account for that timeout.

## Test Signals

Relevant tests include SPQ allocation/setup/free under probe/remove, posting CB and EBLOCK ramrods, forcing ring exhaustion to exercise `unlimited_pending`, injecting out-of-order completions to verify bitmap advancement, validating doorbell recovery registration/removal, EQ async dispatch to SR-IOV, CQE-based Ethernet ramrod completion, and failure injection for stuck ramrods that should invoke MCP drain and hardware-error notification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_spq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_sriov.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_sriov.c

## Purpose

`qed_sriov.c` implements PF-side SR-IOV support and the PF/VF mailbox protocol for the QED driver. It discovers SR-IOV PCI capabilities, allocates per-VF mailbox and bulletin DMA resources, enables/disables VF hardware access, processes VF TLV requests, handles VF FLR and malicious indications, synchronizes PF-imposed MAC/VLAN/link/rate/trust settings to VFs, and exposes hypervisor-facing operations through `qed_iov_ops_pass`.

## Important APIs and Functions

- SR-IOV discovery and allocation: `qed_iov_hw_info()`, `qed_iov_pci_cfg_info()`, `qed_iov_alloc()`, `qed_iov_setup()`, `qed_iov_free()`, and `qed_iov_free_hw_info()` populate `cdev->p_iov_info`, allocate `struct qed_pf_iov`, register the common async callback, and build per-VF DMA mailboxes and bulletins.
- VF database setup: `qed_iov_setup_vfdb()` initializes each `struct qed_vf_info` with mailbox offsets, bulletin memory, relative/absolute VF IDs, concrete and opaque FIDs, vport IDs, filter limits, and initial `VF_STOPPED` state.
- VF hardware lifecycle: `qed_iov_init_hw_for_vf()`, `qed_iov_release_hw_for_vf()`, `qed_iov_enable_vf_access()`, `qed_iov_enable_vf_traffic()`, `qed_sp_vf_start()`, and `qed_sp_vf_stop()` allocate IGU status blocks, program queue permissions, initialize VF hardware, start/stop firmware VF contexts, and clear runtime state.
- Mailbox/TLV helpers: `qed_add_tlv()`, `qed_dp_tlv_list()`, `qed_iov_search_list_tlvs()`, `qed_iov_send_response()`, `qed_iov_prepare_resp()`, and `qed_iov_prep_vp_update_resp_tlvs()` build and validate PF/VF messages.
- Mailbox request handlers cover acquire, vport start/stop/update, RX/TX queue start/stop/update, unicast filters, close, interrupt cleanup, release, tunnel updates, coalesce read/update, and trusted bulletin MAC updates.
- VF validation helpers include `qed_iov_is_valid_vfid()`, `qed_iov_validate_rxq()`, `qed_iov_validate_txq()`, `qed_iov_validate_sb()`, `qed_iov_validate_active_rxq()`, and `qed_iov_validate_active_txq()`.
- FLR and malicious handling: `qed_iov_mark_vf_flr()`, `qed_iov_vf_flr_cleanup()`, `qed_iov_execute_vf_flr_cleanup()`, `qed_sriov_vfpf_malicious()`, and `qed_sriov_eqe_event()`.
- PF/hypervisor operations: `qed_sriov_configure()`, `qed_sriov_enable()`, `qed_sriov_disable()`, `qed_sriov_pf_set_mac()`, `qed_sriov_pf_set_vlan()`, `qed_get_vf_config()`, `qed_set_vf_link_state()`, `qed_spoof_configure()`, `qed_set_vf_rate()`, and `qed_set_vf_trust()`.
- Workqueue plumbing: `qed_schedule_iov()`, `qed_iov_pf_task()`, `qed_iov_wq_start()`, `qed_iov_wq_stop()`, and `qed_vf_start_iov_wq()`.

## Control Flow

Probe-time SR-IOV preparation starts with PCI capability discovery in `qed_iov_hw_info()`. If the PF exposes total VFs, the driver allocates `qed_hw_sriov_info`, computes the first VF ID in the PF, allocates PF IOV state, registers `qed_sriov_eqe_event()` as the common async callback, and allocates coherent mailbox, reply, and bulletin arrays. `qed_iov_setup()` then slices those arrays per VF and initializes identity/resource fields in `vfs_array`.

Enabling SR-IOV through `qed_sriov_configure()` calls `qed_sriov_enable()`. For every hardware function, it computes equal queue distribution, acquires PTT, validates requested queue zones, allocates IGU SBs, records VF RX/TX queue IDs, writes current link state into the bulletin, enables VF internal access, and finally calls `pci_enable_sriov()`. Disabling flushes IOV workqueues, marks VFs as disabling, optionally calls `pci_disable_sriov()`, cleans WFQ state, waits for VFs to stop, releases VF hardware resources, and clears the disabling mark.

VF mailbox traffic is event driven. A firmware EQE with `COMMON_EVENT_VF_PF_CHANNEL` enters `qed_sriov_eqe_event()`, which records the VF request DMA address and schedules `QED_IOV_WQ_MSG_FLAG`. The PF workqueue copies the VF request into the PF mailbox buffer via DMAE, validates the first TLV, dispatches by TLV type in `qed_iov_process_mbx_req()`, builds a response TLV list, copies the response to VF memory, sets the channel-ready bit, and finally copies the first response word so the VF can continue.

The acquire flow negotiates HSI version and capabilities, stores the VF acquire message, records the VF bulletin address, reports PF device and resource information, starts the VF firmware context with `COMMON_RAMROD_VF_START`, posts the initial bulletin, and moves the VF to `VF_ACQUIRED`. Vport and queue flows then create a vport, enable queue permission and interrupts, start RX/TX queue ramrods, update RSS/TPA/acceptance settings, and maintain per-queue CIDs for later stop/update/coalesce operations.

PF-imposed configuration is asynchronous. Hypervisor ops update public VF info fields and schedule IOV flags. The workqueue applies forced or trusted MACs, forced VLAN/PVID, bulletin updates, trust-mode changes, spoof-check changes, link-state changes, and rate limiting across all active hardware functions.

FLR handling records pending FLR bits from MFW, schedules cleanup, polls DORQ and PBF drain conditions, calls final cleanup, resets the VF-PF channel-ready bit, re-enables VF access, acknowledges MFW, and clears mailbox pending state.

## State and Persistence Behavior

All state is volatile driver, PCI, firmware, or DMA state. `cdev->p_iov_info` stores device-wide SR-IOV PCI capability information and active VF count. Each PF hardware function owns `pf_iov_info`, including `vfs_array`, pending FLR bitmaps, coherent mailbox buffers, coherent reply buffers, and coherent bulletin memory. Each `qed_vf_info` tracks VF state, mailbox pending state, acquisition data, concrete/opaque FIDs, vport and queue resources, IGU SBs, active RX count, public hypervisor-facing settings, spoof-check state, shadow MAC/VLAN configuration, and configured bulletin features.

Bulletins are PF-owned DMA-backed records copied into VF memory. The PF increments bulletin version, recomputes CRC, and posts via DMAE. Shadow MAC/VLAN state is used to restore VF-requested filters when PF-forced MAC/VLAN settings are removed or trust mode changes.

Workqueue flags in `hwfn->iov_task_flags` persist pending asynchronous PF work until `qed_iov_pf_task()` clears and handles them. `qed_schedule_iov()` uses memory barriers around atomic bit setting before queueing work.

## Dependencies and Integration Points

This file integrates with PCI SR-IOV config space, Linux workqueues, DMA coherent allocation, DMAE copy helpers, MCP link and FLR acknowledgement APIs, PTT register access, IGU/CAU interrupt programming, queue CID allocation, Ethernet vport/queue/filter slow-path ramrods, tunnel PF update ramrods, WFQ/rate-limit configuration, and firmware event-ring dispatch through the SPQ async callback table.

It is tightly coupled to `qed_sriov.h` structures, `qed_vf.h` TLV definitions, `qed_sp.h`/`qed_spq.c` for common and VF ramrods, Ethernet slow-path functions for vport and queue management, and the public `linux/qed/qed_iov_if.h` hypervisor interface.

## Risks and Edge Cases

- `qed_iov_allocate_vfdb()` returns immediately on later DMA allocation failures without freeing earlier allocations in that function. Callers may clean up later, but partial allocation paths deserve careful review.
- `qed_iov_get_next_active_vf()` loops with `i` but calls `qed_iov_is_valid_vfid()` using `rel_vf_id`, not `i`. This works for contiguous enabled VFs starting at the requested ID but can fail to skip inactive holes and can affect `qed_for_each_vf()` users.
- Mailbox parsing protects against zero-length and overrun TLVs, but every new TLV handler must preserve length, qid, queue-state, and trust validation because VF input is untrusted.
- Several PF policy changes are asynchronous through workqueue flags. Races between VF mailbox requests, PF forced MAC/VLAN updates, trust changes, and FLR cleanup can produce subtle state-ordering bugs.
- VF state transitions are distributed across mailbox handlers, enable/disable, FLR, and release. Incorrect ordering can leave a VF with live queue CIDs, enabled permissions, or stale bulletin state after stop or FLR.
- Forced VLAN handling rewrites vport default VLAN, silent stripping, and all active RX queues. Failures midway can leave filter, vport, and queue settings partially updated.
- Tunnel update validation modifies request state and may update bulletins and client port state even when the VF receives failure for unsupported/partial requests.
- `qed_sriov_disable()` may wait up to roughly two seconds per VF for FLR/stop state; teardown and recovery paths need to tolerate long waits and PTT acquisition failure.
- Trusted VF behavior intentionally lets VFs configure broader receive modes and bulletin MAC updates. Trust transition code must keep shadow MAC state coherent when toggling trust on and off.

## Test Signals

High-value tests include enabling/disabling SR-IOV for different VF counts, mailbox acquire with legacy and current HSI VFs, vport start/stop, RX/TX queue start/stop/update with queue-QID and legacy modes, RSS table validation with invalid VF queues, forced MAC/VLAN and trust toggling while VFs are running, spoof-check changes before and after vport start, link-state and rate-limit propagation through bulletins, VF FLR during active queues, malicious VF indications blocking later mailbox commands, tunnel update requests from VFs, and teardown under recovery mode. Runtime signals include clean bulletin CRC/version updates, no leaked queue CIDs after release/FLR, no stuck pending mailbox bits, and successful MFW FLR acknowledgements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_sriov.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_sriov.h

## Purpose

`qed_sriov.h` declares the internal SR-IOV PF/VF data model and APIs for the QED driver. It defines compile-time PF/VF mode macros, VF resource limits, public hypervisor-visible VF state, per-VF mailbox and queue structures, PF-owned SR-IOV state, workqueue flags, SR-IOV exported functions, and no-op stubs when `CONFIG_QED_SRIOV` is disabled.

## Important APIs, Types, and Data Structures

- Mode macros: `IS_VF(cdev)`, `IS_PF(cdev)`, `IS_PF_SRIOV(p_hwfn)`, and `IS_PF_SRIOV_ALLOC(p_hwfn)` abstract VF/PF and allocation checks across SR-IOV and non-SR-IOV builds.
- Limits: `QED_ETH_VF_NUM_MAC_FILTERS`, `QED_ETH_VF_NUM_VLAN_FILTERS`, `QED_MAX_VF_CHAINS_PER_PF`, `QED_ETH_MAX_VF_NUM_VLAN_FILTERS`, and `QED_VF_ARRAY_LENGTH`.
- `enum qed_iov_vport_update_flag` maps parsed extended vport-update TLVs to response bits.
- `struct qed_public_vf_info` stores PF/hypervisor-facing policy and query state: forced MAC/VLAN, current VF MAC, link state, TX rate, trust request/configuration, cached accept modes, and accept-any-VLAN.
- `struct qed_iov_vf_init_params` carries VF hardware initialization requests, including relative VF ID, number of queues, and PF-relative RX/TX queue IDs.
- `struct qed_hw_sriov_info` stores device-wide PCI SR-IOV capability fields and `first_vf_in_pf`.
- `struct qed_iov_vf_mbx` stores per-VF request/reply coherent mailbox pointers, DMA addresses, pending VF request address, pending flag, TLV offset, and first TLV snapshot.
- `struct qed_vf_queue_cid`, `struct qed_vf_queue`, and queue ID constants model RX/TX queue-zone CIDs, including legacy queue-ID compatibility.
- `enum vf_state` defines VF lifecycle states: `VF_FREE`, `VF_ACQUIRED`, `VF_ENABLED`, `VF_RESET`, and `VF_STOPPED`.
- `struct qed_vf_shadow_config` tracks guest VLAN and MAC configuration so PF-forced settings can be applied and later restored.
- `struct qed_vf_info` is the main per-VF state object, containing mailbox state, lifecycle flags, malicious/disable flags, bulletin memory, acquisition data, FIDs, vport/queue/SB resources, coalesce settings, public policy state, spoof-check state, shadows, and configured bulletin feature bits.
- `struct qed_pf_iov` stores the per-hwfn VF array, pending FLR bitmaps, and contiguous DMA allocations for request mailboxes, reply mailboxes, and bulletins.
- `enum qed_iov_wq_flag` enumerates asynchronous PF/VF workqueue tasks for mailbox messages, PF unicast updates, bulletin posts, stop, FLR, trust changes, and VF force-link queries.
- The header exports `qed_iov_ops_pass` and SR-IOV helpers such as `qed_iov_hw_info`, `qed_iov_alloc/setup/free`, `qed_iov_mark_vf_flr`, `qed_sriov_eqe_event`, `qed_sriov_disable`, `qed_inform_vf_link_state`, and TLV helpers.

## Control Flow

The header supports three major flows. First, hardware discovery and allocation flow through `qed_iov_hw_info()`, `qed_iov_alloc()`, `qed_iov_setup()`, and matching free functions. Second, runtime mailbox and event handling flow through `qed_sriov_eqe_event()`, `qed_iov_search_list_tlvs()`, `qed_add_tlv()`, `qed_dp_tlv_list()`, and scheduled IOV work. Third, PF/hypervisor control flows use `qed_iov_ops_pass` operations, bulletin setters, FLR marking, link-state notification, and SR-IOV disable.

When SR-IOV is disabled at compile time, the same call sites compile through static inline stubs that return neutral values (`false`, `0`, `MAX_NUM_VFS`) and perform no side effects. This keeps common PF and SPQ code from carrying extensive `#ifdef` branches.

## State and Persistence Behavior

The structures declared here define all PF-side SR-IOV runtime persistence. `qed_hw_sriov_info` is device-wide and exists if PCI SR-IOV capability is usable. `qed_pf_iov` is per hardware function and exists after allocation. `qed_vf_info` entries persist across VF acquire/release cycles so PF policy, mailbox buffers, bulletins, and resource ownership can be reused and reset.

The header separates public VF policy (`qed_public_vf_info`) from internal VF resource state (`qed_vf_info`). Public settings can be changed by PF/hypervisor operations and later applied asynchronously to firmware and bulletins. Shadow config persists VF-requested MAC/VLAN state across forced-mode changes.

## Dependencies and Integration Points

`qed_sriov.h` includes Linux types and `qed_vf.h` for PF/VF TLV and bulletin structures. It is consumed by `qed_sriov.c`, `qed_sp_commands.c`, `qed_spq.c`, and common driver paths that need to branch between PF and VF behavior. It integrates with `struct qed_dev`, `struct qed_hwfn`, `struct qed_iov_hv_ops`, firmware bulletin/TLV definitions, queue CID objects, and workqueue flags stored in the hardware function.

## Risks and Edge Cases

- The header exposes large mutable structs across the driver. Layout changes can affect allocation sizing, DMA mailbox slicing, and assumptions in SR-IOV implementation code.
- `QED_VF_ARRAY_LENGTH` is fixed at 3 for pending FLR/event bitmaps. This assumes the maximum static VF count fits in 192 bits; changes to hardware VF limits must revisit it.
- Compile-time stubs return success for many functions when SR-IOV is disabled. Common callers must not treat those successes as proof that SR-IOV resources exist.
- The distinction between `IS_PF_SRIOV()` and `IS_PF_SRIOV_ALLOC()` matters. Capability discovery and per-hwfn allocation occur at different stages, and using the wrong predicate can dereference missing state.
- Per-VF state includes both `is_trusted_request` and `is_trusted_configured`; code must not conflate requested policy with applied policy.
- `configured_features` uses bulletin valid-map bit positions. New bulletin fields must avoid bit collisions and update `QED_IOV_CONFIGURED_FEATURES_MASK` if they represent PF-configured features.

## Test Signals

Header-level validation is mostly build and integration driven: all SR-IOV and non-SR-IOV configurations should compile, PF-only builds should exercise static stubs without side effects, SR-IOV builds should allocate `qed_pf_iov` and per-VF data correctly for maximum VF counts, FLR bitmaps should cover all supported VFs, and hypervisor ops should observe public VF state transitions accurately through `qed_get_vf_config()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_sriov.h -->
