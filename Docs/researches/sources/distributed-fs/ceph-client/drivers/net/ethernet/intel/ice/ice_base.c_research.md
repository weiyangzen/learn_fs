# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_base.c

## Purpose

`ice_base.c` is the Intel ICE driver's VSI queue bring-up and queue-pair control implementation. It owns the local Linux-side preparation of Rx/Tx rings, maps VSI rings to interrupt vectors, allocates and frees `ice_q_vector` instances, programs queue interrupt registers, constructs RLAN/TLAN/TxTime queue contexts, calls the common AdminQ scheduler helpers to add or remove Tx queues, and provides single queue-pair disable/enable routines used by AF_XDP and dynamic queue operations.

This file is not a standalone hardware abstraction. It sits between high-level VSI/netdev orchestration in `ice_lib.c`, DCB/SR-IOV/XDP helpers, and lower-level register/AdminQ routines from `ice_common.c`.

## Important APIs, Types, and Functions

Exported entry points:

- `ice_vsi_cfg_single_rxq()` and `ice_vsi_cfg_rxqs()` configure one or all Rx rings, including XSK/page-pool setup, XDP RXQ metadata, RLAN context programming, tail pointer initialization, and initial buffer posting.
- `__ice_vsi_get_qs()` assigns PF-global queue IDs to a VSI using contiguous allocation first and scattered allocation as fallback.
- `ice_vsi_ctrl_one_rx_ring()` and `ice_vsi_wait_one_rx_ring()` request Rx queue enable/disable and optionally wait for `QRX_CTRL_QENA_STAT_M`.
- `ice_vsi_alloc_q_vectors()`, `ice_vsi_map_rings_to_vectors()`, and `ice_vsi_free_q_vectors()` allocate interrupt vector containers, register NAPI when a netdev exists, map rings evenly to vectors, and clean up interrupt/NAPI ownership.
- `ice_vsi_cfg_single_txq()`, `ice_vsi_cfg_lan_txqs()`, and `ice_vsi_cfg_xdp_txqs()` configure Tx rings through TLAN contexts and scheduler/AdminQ queue-add calls.
- `ice_cfg_itr()`, `ice_cfg_txq_interrupt()`, `ice_cfg_rxq_interrupt()`, and `ice_trigger_sw_intr()` program interrupt throttling, queue interrupt causes, and software interrupt triggers.
- `ice_vsi_stop_tx_ring()` and `ice_fill_txq_meta()` prepare and issue Tx queue disable requests.
- `ice_qp_dis()` and `ice_qp_ena()` implement one queue-pair teardown/restart, including netdev queue state, NAPI/IRQ toggles, Rx/Tx hardware control, ring cleaning, stats reset, XDP pool refresh, and carrier handling.
- `ice_calc_ts_ring_count()` derives a timestamp queue descriptor count from E830 TxTime fetch profile registers.

Key local helpers:

- `__ice_vsi_get_qs_contig()` and `__ice_vsi_get_qs_sc()` manipulate PF queue allocation bitmaps under `qs_cfg->qs_mutex`.
- `ice_vsi_alloc_q_vector()` handles vector allocation variants for PF, VF, loopback, and VF control VSIs.
- `ice_setup_tx_ctx()` and `ice_setup_txtime_ctx()` fill CPU-side queue context structs before common-layer packing.
- `ice_setup_rx_ctx()` fills `struct ice_rlan_ctx`, handles DVM/VF VLAN descriptor compatibility, switchdev descriptor selection, RLAN programming, and Rx tail setup.
- `ice_rxq_pp_create()` creates libeth page-pool fill queues, optionally with a separate header-split pool.
- `ice_vsi_cfg_txq()` builds an AdminQ add-Tx-queue group, calls `ice_ena_vsi_txq()`, records firmware TEIDs, and optionally configures a Tx timestamp queue.

## Control Flow

Queue allocation starts with `__ice_vsi_get_qs()`. The driver attempts a contiguous zero region in the PF queue bitmap; if that fails, it lowers `q_count` to `scatter_count`, marks `mapping_mode = ICE_VSI_MAP_SCATTER`, and assigns individual free bits. The scattered rollback path clears bits assigned in the current attempt and zeros corresponding VSI map entries.

Interrupt setup starts with `ice_vsi_alloc_q_vectors()`, which loops over `vsi->num_q_vectors`. `ice_vsi_alloc_q_vector()` creates an `ice_q_vector`, initializes default dynamic ITR state, derives VF register indexes for VF VSIs, reuses a control-VSI interrupt for VF control VSIs where appropriate, or allocates a PF IRQ with `ice_alloc_irq()`. If a netdev already exists, NAPI is registered immediately. Ring-to-vector mapping then distributes remaining Tx and Rx rings over remaining vectors with `DIV_ROUND_UP`, links rings into each vector's Tx/Rx container lists, sets ITR indexes, and maps XDP rings when XDP is enabled.

Rx configuration flows from `ice_vsi_cfg_rxqs()` to `ice_vsi_cfg_rxq()`. PF/SF/LB rings first choose any AF_XDP pool and either register an XSK memory model or create page-pool fill queues and attach the page pool to XDP RXQ metadata. `ice_setup_rx_ctx()` then prepares the RLAN context using ring DMA, descriptor count, buffer size, CRC strip flags, VLAN/DVM behavior, header-split fields, max frame constraints, descriptor prefetch, and switchdev descriptor ID. It writes the hardware context with `ice_write_rxq_ctx()`, then assigns and clears the per-queue tail register for non-VF queues. After context setup, the function posts XSK zero-copy buffers, control-Rx descriptors, or regular Rx buffers.

Tx configuration flows through `ice_vsi_cfg_txqs()` or `ice_vsi_cfg_single_txq()` into `ice_vsi_cfg_txq()`. The ring's XPS mapping is initialized once, `ice_setup_tx_ctx()` fills the TLAN context, `ice_pack_txq_ctx()` packs it into the add-queue buffer, the software queue handle is calculated per TC/channel, and `ice_ena_vsi_txq()` adds the queue into firmware and the scheduler tree. Firmware's queue TEID response is copied back to the ring. If TxTime is enabled, the code allocates a timestamp ring, fills/packs its context, sets the doorbell, and calls `ice_aq_set_txtimeq()`. If timestamp setup fails after the LAN queue was enabled, it frees the timestamp ring and disables the LAN Tx queue to avoid leaving a partially configured queue.

Queue-pair disable in `ice_qp_dis()` synchronizes networking, drops carrier, stops the netdev Tx queue, disables IRQ/NAPI, disables the regular Tx ring and optional XDP Tx ring, requests Rx disable without waiting, cleans all rings, and resets per-ring stats. Queue-pair enable reverses this path by configuring Tx/XDP/Rx rings, programming MSI-X mapping, enabling Rx with a wait, enabling NAPI/IRQ, synchronizing XSK pointer visibility with `synchronize_net()`, and starting the netdev queue if link is up.

## State and Persistence Behavior

Persistent driver state updated here includes:

- PF queue bitmap allocation and VSI `txq_map`/`rxq_map` arrays through `__ice_vsi_get_qs()`.
- `vsi->q_vectors[]`, q-vector interrupt identities, NAPI registration, and ring `q_vector` linked-list membership.
- Ring fields such as `tail`, `q_handle`, `txq_teid`, XDP RXQ registration, page-pool pointers, header-split pool metadata, `xps_state`, and timestamp ring ownership.
- Hardware registers including `GLINT_CTL`, `QINT_TQCTL`, `QINT_RQCTL`, `QRX_CTRL`, `QRX_TAIL`, `QTX_COMM_DBELL`, and E830 TxTime doorbell registers.
- Firmware/scheduler state through `ice_ena_vsi_txq()`, `ice_dis_vsi_txq()`, and `ice_aq_set_txtimeq()`.

The file assumes context ownership is coordinated by the higher-level VSI lifecycle. It takes local locks for PF queue bitmap assignment but generally relies on caller sequencing for ring arrays, NAPI toggles, and queue pair operations.

## Dependencies and Integration Points

Direct dependencies include:

- `ice_common.c` for queue context packing/writes, Tx queue add/remove, TxTime AdminQ, link status, and scheduler-facing queue contexts.
- `ice_lib.c` and related VSI helpers for ring allocation, `ice_qvec_*()` IRQ/NAPI operations, XDP mapping, ring cleaning, and hardware VSI numbers.
- `ice_dcb_lib.h` for DCB traffic class decisions.
- `ice_sriov.h` and VF helpers for VF register indexing, port VLAN behavior, VF control VSI interrupt sharing, and VF-disable checks.
- Linux networking APIs: NAPI, XDP RXQ metadata, AF_XDP pool operations, page-pool/libeth fill queues, XPS, `netif_tx_*`, and carrier state.
- Device registers and AdminQ structures declared in ICE hardware headers.

## Risks and Edge Cases

- The scattered queue allocation rollback clears `qs_cfg->vsi_map[index]` instead of consistently using `index + vsi_map_offset` for the PF bitmap lookup in the first clear operation. The subsequent zeroing uses the offset. Any future changes here should verify rollback against nonzero `vsi_map_offset`.
- `ice_vsi_alloc_q_vectors()` can partially succeed and returns success when at least one vector was allocated, while shrinking `vsi->num_q_vectors`. Callers must tolerate fewer vectors than originally requested.
- `ice_vsi_cfg_rxq()` has multiple setup paths where XDP RXQ metadata, page pools, and XSK pool state must be unwound correctly. Error labels destroy fill queues but do not explicitly unregister every XDP RXQ state in this snippet, so callers and companion cleanup paths matter.
- `ice_vsi_ctrl_one_rx_ring()` does not bounds-check `rxq_idx`; public callers that accept external indexes must validate first.
- Tx timestamp setup is a partial-failure-sensitive path: LAN Tx queue add succeeds before timestamp queue setup. The cleanup path disables the Tx queue, but tests should verify TEID/q_handle state after failure.
- `ice_calc_ts_ring_count()` loops over `ICE_TXTIME_FETCH_PROFILE_CNT` but reads `E830_GLTXTIME_FETCH_PROFILE(prof, 0)` with `prof` fixed to zero. If multiple profiles are expected, this may be deliberate hardware behavior or a latent oversight worth checking against datasheet intent.
- Queue-pair disable asks Rx to stop without waiting, then immediately cleans rings. Higher-level users must ensure no in-flight DMA or polling race remains beyond the IRQ/NAPI disable and `synchronize_net()` ordering.

## Test Signals

Useful validation signals include:

- Build coverage with `CONFIG_DCB`, `CONFIG_XDP_SOCKETS`, SR-IOV, switchdev, and Tx timestamping variants.
- Queue bring-up smoke tests: create PF VSI, enable traffic, enable/disable a single queue pair, and verify no Rx/Tx timeout, NAPI leak, IRQ leak, or page-pool leak.
- AF_XDP zero-copy tests for pool bind/unbind and queue-pair restart paths.
- VF and VF control VSI tests to confirm interrupt sharing and VM/VF queue context fields.
- DCB traffic-class tests to verify `q_handle` calculations and scheduler placement.
- Fault injection for `ice_ena_vsi_txq()`, `ice_aq_set_txtimeq()`, page-pool creation, and buffer allocation failures.
- Register/AdminQ tracing around `QRX_CTRL`, `QINT_*`, Tx queue TEIDs, and scheduler node add/remove during reset and queue-pair operations.
