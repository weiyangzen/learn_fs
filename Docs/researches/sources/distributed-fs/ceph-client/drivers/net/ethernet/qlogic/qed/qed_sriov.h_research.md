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
