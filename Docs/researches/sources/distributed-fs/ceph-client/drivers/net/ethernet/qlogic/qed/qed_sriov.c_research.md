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
