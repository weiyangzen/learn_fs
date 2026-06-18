# subset-b-004354 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hw_def.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hw_def.h

## Purpose
This header defines hardware descriptor and completion layouts for the Broadcom `bnge` network driver. It is the low-level contract used by TX, RX, TPA/GRO, RSS, VLAN, checksum, and asynchronous-event paths to encode or decode values shared with firmware and NIC DMA rings.

## Important APIs, Types, And Functions
The exported surface is macro-heavy. Important structures are `tx_bd_ext`, `rx_cmp`, `rx_cmp_ext`, `rx_agg_cmp`, `rx_tpa_start_cmp`, `rx_tpa_start_cmp_ext`, `rx_tpa_end_cmp`, and `rx_tpa_end_cmp_ext`. Important helpers include `TX_CMP_SQ_CONS_IDX`, `RX_CMP_L4_CS_OK`, `RX_CMP_METADATA0_TCI`, `RX_CMP_V3_HASH_TYPE`, `RX_CMP_VLAN_VALID`, `RX_CMP_HASH_TYPE`, `TPA_START_*`, `TPA_END_*`, and async-event decoding helpers such as `EVENT_DATA1_RESET_NOTIFY_FATAL`.

## Control Flow
There is no executable control flow beyond macro expansion. Runtime paths in `bnge_txrx.c`, `bnge_netdev.c`, and HWRM event handling read DMA completions into these packed layouts, mask little-endian fields, and translate them into SKB checksum status, VLAN metadata, RSS hash type, TPA aggregation bookkeeping, and link/reset event handling.

## State And Persistence
The file defines transient hardware-visible ring state. State persists only in DMA descriptors and completion memory populated by the NIC. Valid bits, opaque indices, aggregate IDs, VLAN tags, and error bitfields must be interpreted against the producer/consumer ring indices held in `bnge_net` ring structures.

## Dependencies And Integration Points
It depends on Linux bit helpers, endian helpers, and HSI constants from `<linux/bnge/hsi.h>` included through adjacent headers. `bnge_netdev.h` includes this header so ring structures and NAPI/TXRX code can share descriptor constants.

## Risks
The largest risk is bitfield drift against firmware/HW specifications. Endian mistakes or incorrect masks can silently corrupt packet metadata. `RX_TPA_END_CMP_FLAGS_PLACEMENT_ANY_GRO` uses a bitwise AND of two placement constants; reviewers should confirm this matches the intended hardware encoding. TPA and RSS-v3 macros also depend on capability bits in `bnge_dev`.

## Test Signals
Useful signals are RX/TX traffic with checksum offload, VLAN strip/insert, RSS hash reporting, GRO/LRO/TPA traffic, jumbo frames, tunnel traffic, and async reset/link events. Packet counters, SKB checksum status, VLAN tags, and absence of DMA/completion errors are the practical validation points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hw_def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hwrm.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hwrm.c

## Purpose
This file implements the generic Host Wire Resource Manager request engine. It allocates DMA-backed request/response buffers, validates request ownership with a sentinel, sends commands through the CHIMP mailbox registers, waits for completion or polled response validity, maps firmware errors to Linux errno values, and cleans up HWRM resources.

## Important APIs, Types, And Functions
Public APIs include `bnge_init_hwrm_resources`, `bnge_cleanup_hwrm_resources`, `bnge_hwrm_req_create`, `bnge_hwrm_req_init`, `bnge_hwrm_req_hold`, `bnge_hwrm_req_drop`, `bnge_hwrm_req_flags`, `bnge_hwrm_req_timeout`, `bnge_hwrm_req_alloc_flags`, `bnge_hwrm_req_replace`, `bnge_hwrm_req_send`, `bnge_hwrm_req_send_silent`, and `bnge_hwrm_req_dma_slice`. Internal helpers include `bnge_cal_sentinel`, `__hwrm_ctx_get`, `bnge_hwrm_create_token`, `bnge_hwrm_destroy_token`, `bnge_map_hwrm_error`, and `__hwrm_send_ctx`.

## Control Flow
Callers allocate a typed HWRM request with `bnge_hwrm_req_init`, optionally hold the response buffer, populate command-specific fields, then call `bnge_hwrm_req_send`. `__hwrm_send_ctx` creates a wait token under `bd->hwrm_cmd_lock`, assigns a sequence ID, writes the request window to BAR0, rings the CHIMP doorbell, and either waits for completion-ring processing or polls `resp_len` and the response valid byte. On exit it destroys the token and either invalidates the context or leaves it owned for callers that held the response.

## State And Persistence
The persistent driver state is `bd->hwrm_dma_pool`, `bd->hwrm_pending_list`, `bd->hwrm_cmd_seq`, `bd->hwrm_cmd_kong_seq`, and command timeout/capability fields populated elsewhere. Per-command state is held in `struct bnge_hwrm_ctx`, including DMA address, request length, response dirty flag, timeout, optional coherent DMA slice, and ownership flags.

## Dependencies And Integration Points
It integrates with every HWRM command wrapper in `bnge_hwrm_lib.c`, link management, ring allocation, and resource setup. It uses Linux DMA pools, coherent DMA, RCU hlist deletion for pending CHIMP tokens, PCI BAR I/O, memory barriers, and HSI `struct input`/`struct output`.

## Risks
Risks concentrate around lifetime and concurrency: invalid requests are caught only by the sentinel, held responses must be dropped, command buffers can be reused with `bnge_hwrm_req_replace`, and cleanup marks pending tokens cancelled after destroying the DMA pool. Timeout math and response valid-byte handling are hardware-sensitive. DMA slices allow only one external allocation per context, so callers must size requests correctly.

## Test Signals
Probe-time HWRM version, function capability, resource, link, ring, VNIC, and stats commands provide coverage. Fault signals include timeout logs, out-of-sequence response warnings, busy firmware warnings, sentinel mismatch dumps, and leaked or double-dropped request contexts under error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hwrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hwrm.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hwrm.h

## Purpose
This header declares the HWRM request context model, wait-token state machine, mailbox channel constants, timeout constants, DMA layout, and public request APIs used by all firmware-command wrappers.

## Important APIs, Types, And Functions
Important types are `enum bnge_hwrm_ctx_flags`, `struct bnge_hwrm_ctx`, `enum bnge_hwrm_wait_state`, `enum bnge_hwrm_chnl`, and `struct bnge_hwrm_wait_token`. Important constants define the DMA pool layout: `BNGE_HWRM_DMA_SIZE`, `BNGE_HWRM_RESP_OFFSET`, `BNGE_HWRM_CTX_OFFSET`, `BNGE_HWRM_DMA_ALIGN`, and `BNGE_HWRM_SENTINEL`. `bnge_hwrm_timeout` converts polling loops into approximate elapsed microseconds for diagnostics.

## Control Flow
The header supports a create/populate/send/drop flow. `bnge_hwrm_req_init` wraps `bnge_hwrm_req_create` with the typed request size. Callers may use `bnge_hwrm_req_hold` to keep the response valid across send, `bnge_hwrm_req_dma_slice` to reserve command-adjacent DMA, and `bnge_hwrm_req_flags` or `bnge_hwrm_req_timeout` to alter send behavior.

## State And Persistence
The context state is per request and lives inside the DMA allocation. Flags distinguish internal ownership, dirty held responses, silent error logging, and full waits. Wait tokens live on the device pending list for CHIMP completions and carry sequence IDs and state transitions from pending to deferred, complete, or cancelled.

## Dependencies And Integration Points
The header depends on `<linux/bnge/hsi.h>` for common HWRM input/output layouts. It is included by command wrappers, resource setup, link management, and netdev initialization. It assumes `struct bnge_dev` has HWRM timeout, DMA pool, and pending-list members.

## Risks
The layout constants assume a two-page DMA object where request, context, and response do not overlap. Any request larger than `BNGE_HWRM_CTX_OFFSET` is invalid. The API is intentionally `void *` based, so type safety relies on caller discipline and runtime sentinel validation.

## Test Signals
Compilation with HSI structures is the first guard. Runtime coverage comes from commands that hold responses, commands that need custom timeouts, replacement of requests for larger messages, and commands requiring DMA slices such as tables or backing-store configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hwrm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hwrm_lib.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hwrm_lib.c

## Purpose
This file provides command-specific HWRM wrappers above the generic request engine. It discovers firmware version and capabilities, registers the driver, configures backing-store memory, reserves rings, allocates VNIC/RSS/filter/stat/ring resources, configures PHY/link/TPA, and queries port/function statistics.

## Important APIs, Types, And Functions
Key public functions are `bnge_hwrm_ver_get`, `bnge_hwrm_func_reset`, `bnge_hwrm_fw_set_time`, `bnge_hwrm_func_drv_rgtr`, `bnge_hwrm_func_drv_unrgtr`, `bnge_hwrm_func_qcaps`, `bnge_hwrm_func_qcfg`, `bnge_hwrm_func_resc_qcaps`, `bnge_hwrm_vnic_qcaps`, `bnge_hwrm_queue_qportcfg`, `bnge_hwrm_func_backing_store_qcaps`, `bnge_hwrm_func_backing_store`, `bnge_hwrm_reserve_rings`, VNIC helpers, L2 filter helpers, ring alloc/free helpers, stats helpers, and link helpers. Internal helpers translate firmware capability responses into `bd` and `bn` fields.

## Control Flow
Probe paths first call version/capability queries, driver registration, function/resource queries, queue configuration, and backing-store capability setup. Open paths allocate stat contexts, rings, VNICs, RSS contexts, filters, and TPA configuration. Link paths use PHY qcaps/qcfg/cfg wrappers to update cached link state and apply ethtool requests. Stats paths query counter masks and trigger DMA updates.

## State And Persistence
The file populates persistent firmware-derived state in `struct bnge_dev`: firmware version strings, HWRM limits, chip ID, capability flags, PF identity, maximum MTU, doorbell aperture, resource maxima/reservations, RSS capability, queue mapping, PHY flags, and backing-store context metadata. It also updates `bnge_net` VNIC IDs, RSS context IDs, stat context IDs, ring firmware IDs, filter IDs, TPA settings, and stats sizes.

## Dependencies And Integration Points
It depends on `bnge_hwrm.c` for command transport, `bnge_rmem.c` for backing-store page tables, `bnge_resc.c` for ring-count calculations, `bnge_link.c` for common link request field construction, and `bnge_netdev.c` for ring/VNIC data structures. It uses HSI command structures heavily.

## Risks
Many functions assume firmware responses are internally consistent. Ring reservation has to reconcile TX, RX, completion, IRQ, stat, VNIC, and RoCE resource counts. Backing-store qcaps iteration depends on `next_valid_type`; a bad response can skip types or leave partially allocated `bd->ctx`. Resource-free helpers generally log and continue, so firmware/local ID skew is possible after failed cleanup.

## Test Signals
Probe/open/close cycles, ethtool link changes, RSS enablement, multicast/unicast filter updates, RoCE-enabled and disabled configurations, jumbo/GRO/LRO traffic, and stats collection exercise most wrappers. HWRM error injection should produce mapped errno values and clean local rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hwrm_lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hwrm_lib.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hwrm_lib.h

## Purpose
This header declares the command-specific HWRM helper layer used by probe, resource management, netdev open/close, VNIC setup, ring setup, stats, and link management.

## Important APIs, Types, And Functions
The declarations cover version/reset/time/driver registration, VNIC qcaps and configuration, NVM device info, backing-store qcaps/config, ring reservation, function qcaps/qcfg/resource qcaps, queue qportcfg, VNIC HDS/RSS/config/allocation/free, L2 filter allocation/free/mask, stat context allocation/free, ring allocation/free, async event completion-ring setup, TPA setup, link update/config/shutdown, and port/function stats queries.

## Control Flow
The header establishes the ordering used elsewhere: discover firmware capabilities, allocate backing-store memory, reserve resources, allocate software memory, allocate firmware rings/stat/VNIC/RSS/filter objects, enable link/TPA, then reverse those operations during close or remove.

## State And Persistence
No state is stored in the header. Its API mutates `struct bnge_dev`, `struct bnge_net`, `struct bnge_vnic_info`, `struct bnge_l2_filter`, `struct bnge_ring_struct`, and stats memory according to firmware command results.

## Dependencies And Integration Points
It depends on HSI constants and adjacent driver structures. `bnge_netdev.c`, `bnge_resc.c`, `bnge_rmem.c`, and `bnge_link.c` are the main consumers. The macros `BNGE_PLC_EN_*` and `BNGE_VNIC_CFG_ROCE_DUAL_MODE` alias HSI fields for local naming.

## Risks
The API is broad and has mixed ownership conventions: some functions allocate firmware IDs, some free them, some only query and cache capabilities, and some silently ignore unsupported optional features. Callers must pair allocation/free functions carefully and must not use firmware IDs after they are reset to invalid values.

## Test Signals
Build coverage catches mismatched prototypes. Runtime coverage should include full probe/open/close, link configuration, stats query, RSS setup, filter updates, and error paths where a later allocation fails after earlier firmware objects were created.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_hwrm_lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_link.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_link.c

## Purpose
This file translates firmware PHY/link state into Linux ethtool state and translates ethtool link requests back into HWRM PHY configuration fields. It covers speed, lanes, media, signal mode, pause, FEC reporting, module status, and async link-event dispatch.

## Important APIs, Types, And Functions
Public functions include `bnge_init_ethtool_link_settings`, `bnge_probe_phy`, `bnge_hwrm_set_link_common`, `bnge_hwrm_set_pause_common`, `bnge_update_phy_setting`, `bnge_get_port_module_status`, `bnge_support_speed_dropped`, `bnge_report_link`, `bnge_get_link`, `bnge_get_link_ksettings`, `bnge_set_link_ksettings`, and `bnge_link_async_event_process`. Important internal helpers map firmware speed/media/signal values to ethtool modes and back.

## Control Flow
Probe queries PHY capabilities, updates link state, and initializes cached ethtool settings. Link update paths compare requested pause/speed/autoneg state against firmware-reported state, then call HWRM PHY configuration only when changes are needed. `get_link_ksettings` builds supported, advertising, link-partner, FEC, speed, duplex, lanes, and port values. `set_link_ksettings` validates autoneg or forced speed/lane combinations and applies them if the netdev is running.

## State And Persistence
The durable state is split between `bd->link_info`, which mirrors firmware qcfg/qcaps state, and `bn->eth_link_info`, which stores requested ethtool settings. Retry state for failed PHY updates lives in `link_info.phy_retry` and is driven by the netdev timer in `bnge_netdev.c`.

## Dependencies And Integration Points
The file depends on HSI link constants, `bnge_hwrm_lib.c` command wrappers, ethtool linkmode helpers, and netdev carrier state. Async events set bits in `bn->sp_event`; the service task later calls qcaps/qcfg and refreshes ethtool caches.

## Risks
Speed mapping is dense and hardware-generation specific, especially 50G through 800G with NRZ, PAM4 56G, PAM4 112G, media type, and lanes. Advertising masks collapse multiple ethtool media modes into firmware speed bits, so installed media priority matters. Unsupported lane/speed requests must fail without corrupting cached settings.

## Test Signals
Use `ethtool` get/set for autoneg, forced speeds, lanes, pause, and FEC display. Validate link up/down messages, carrier transitions, module warnings, link partner advertising, and async link-speed/config/status events. Hardware with different optics and DAC media is important coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_link.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_link.h

## Purpose
This header defines the driver's cached link-state structures, firmware-to-driver aliases for link speed, pause, autoneg, FEC, and signal mode, plus the link-management API exported to netdev, ethtool, and HWRM wrappers.

## Important APIs, Types, And Functions
Important types are `enum bnge_link_state`, `struct bnge_link_info`, and `struct bnge_ethtool_link_info`. Key macros include `BNGE_PHY_CFG_ABLE`, `BNGE_LINK_IS_UP`, `BNGE_AUTO_MODE`, speed constants for 50G through 800G, speed2 masks, FEC capability/enabled masks, and signal mode constants. Function declarations mirror the public functions in `bnge_link.c`.

## Control Flow
The header supports three flows: firmware query into `bnge_link_info`, ethtool request storage in `bnge_ethtool_link_info`, and HWRM PHY configuration construction from the requested state. Async events enter through `bnge_link_async_event_process`.

## State And Persistence
`bnge_link_info` caches current firmware state including PHY type, media, link status, active lanes, duplex, pause, autoneg mode, speed masks, module status, active FEC, full qcfg response copy, and retry timing. `bnge_ethtool_link_info` persists user-requested autoneg, signal mode, duplex, flow control, speed, advertising mask, and whether a forced link change is pending.

## Dependencies And Integration Points
It includes `<linux/ethtool.h>` and uses HSI constants from included driver headers. It is included by `bnge_netdev.h`, making link state part of the central netdev private structure.

## Risks
The structures are caches, not authoritative hardware state. Callers must refresh with HWRM qcfg/qcaps at the right times. Pause and speed autoneg are tracked separately in a bitmask, which makes partial-autoneg transitions easy to mishandle.

## Test Signals
Compile-time use checks declarations. Runtime test signals are ethtool reporting, link up/down carrier, pause changes, forced-speed settings, module warnings, and PHY retry behavior after failed open-time configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_link.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_netdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_netdev.c

## Purpose
This is the main Linux net_device integration file for `bnge`. It allocates and registers the netdev, owns open/close lifecycle, allocates software and DMA ring memory, programs firmware rings/VNICs/filters/stat contexts, handles NAPI/IRQ setup, manages RX buffer posting, accumulates stats, drives periodic service work, and exposes netdev operations.

## Important APIs, Types, And Functions
Public APIs are `bnge_netdev_alloc`, `bnge_netdev_free`, `bnge_set_ring_params`, `bnge_cp_ring_for_rx`, `bnge_cp_ring_for_tx`, `bnge_fill_hw_rss_tbl`, `bnge_alloc_rx_data`, `bnge_alloc_rx_netmem`, `bnge_find_next_agg_idx`, `__bnge_alloc_rx_frag`, `__bnge_queue_sp_work`, and `bnge_copy_hw_masks`. Important internal clusters cover stats allocation/accumulation, NQ/CP tree allocation, RX/TX ring memory, VNIC attributes, HWRM ring allocation/free, L2 filters, interrupts, NAPI, chip init, open/close, and netdev stat ops.

## Control Flow
`bnge_netdev_alloc` creates the netdev, sets feature flags, initializes workqueue/timer/ring sizing/filter hash/MAC/PHY/stats, and registers it. `ndo_open` calls `bnge_open_core`, which reserves rings, allocates core memory, adds NAPI, requests IRQs, initializes NIC firmware objects, enables NAPI/interrupts/TX, starts the timer, and polls module/link status. `ndo_stop` disables TX, clears open state, deletes the timer, frees firmware resources, disables NAPI, saves stats, frees buffers/IRQs/NAPI/core memory, and shuts down link.

## State And Persistence
The file owns most `struct bnge_net` runtime state: ring sizes/masks, NAPI array, RX/TX rings, NQ/CP tree, group firmware IDs, VNICs, filters, RSS key/table, stats memory, timer/workqueue events, pause/link request cache, and previous stats. Firmware-visible IDs are stored in ring/VNIC/filter/stat fields and reset to invalid on free.

## Dependencies And Integration Points
It depends on `bnge_hwrm_lib.c` for all firmware object operations, `bnge_rmem.c` for ring memory allocation, `bnge_resc.c` for reservation, `bnge_link.c` for PHY updates, `bnge_txrx.c` for poll/xmit, ethtool setup, page_pool, PCI MSI-X, and Linux netdev queue APIs.

## Risks
The open/close error paths are complex and must unwind in exact reverse order. RX page-pool handling differs for unreadable netmem and smaller hardware RX pages. Firmware IDs, doorbells, IRQ vectors, NAPI indices, and queue counts must stay aligned after resource reductions. Stats are accumulated across wrap masks and saved across close, so ordering around `BNGE_STATE_STATS_ENABLE` matters.

## Test Signals
Test probe/register/unregister, repeated open/close, traffic across all queues, jumbo and GRO/LRO/TPA, RSS distribution, multicast/unicast/promisc transitions, MSI-X affinity, IRQ/NAPI teardown races, link retry, stats before and after close, and error injection in ring/VNIC/stat allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_netdev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_netdev.h

## Purpose
This header defines the netdev-facing data model for the `bnge` driver: TX/RX descriptors, completions, software buffer tracking, ring groups, stats memory, NAPI/NQ/CP/RX/TX ring structures, VNIC/filter state, netdev private state, constants, doorbell helpers, and exported netdev helper prototypes.

## Important APIs, Types, And Functions
Core types include `tx_bd`, `rx_bd`, `tx_cmp`, `bnge_sw_tx_bd`, `bnge_sw_rx_bd`, `bnge_sw_rx_agg_bd`, `bnge_ring_grp_info`, `bnge_tpa_info`, `bnge_stats_mem`, `bnge_net`, `bnge_cp_ring_info`, `bnge_nq_ring_info`, `bnge_rx_ring_info`, `bnge_tx_ring_info`, `bnge_napi`, `bnge_vnic_info`, `bnge_filter_base`, `bnge_l2_key`, and `bnge_l2_filter`. Important macros define descriptor counts, ring indexing, completion indexing, stats offsets, queue/TPA limits, NQ handle layout, and doorbell writes.

## Control Flow
The header is passive, but its structures encode runtime control flow. NQ rings own completion rings; completion rings point back to NAPI; RX/TX rings point to their completion ring and doorbell; VNICs point to RSS/filter DMA tables; `bnge_net` ties those pieces to timers, workqueues, feature flags, and stats.

## State And Persistence
Most fields are runtime state allocated on netdev open and freed on close. Persistent across open/close are netdev-level settings such as ring sizes, RSS key validity, previous stats, feature flags, timer/workqueue state, and ethtool link request state. Firmware IDs are invalidated and recreated per open.

## Dependencies And Integration Points
It includes HSI definitions, doorbell definitions, descriptor helpers, and link state. It is consumed by netdev, TX/RX datapath, HWRM command wrappers, resource reservation, and ethtool code.

## Risks
The data model is tightly coupled to queue counts and page-size-derived ring sizes. Incorrect masks or page counts can corrupt ring indexing. `bnge_net` combines many ownership domains, so lifecycle mistakes can become use-after-free across NAPI, IRQ, workqueue, timer, or firmware cleanup paths.

## Test Signals
Compile-time layout use, queue-count changes, RSS table sizing, XDP/page_pool-style RX recycling signals, TPA aggregation, TX completion, NAPI polling, and stat ops are the key coverage areas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_netdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_resc.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_resc.c

## Purpose
This file calculates and reserves hardware resources for the `bnge` function. It balances RX rings, TX rings, completion rings, NQs/MSI-X vectors, VNICs, RSS contexts, stat contexts, and auxiliary RoCE reservations against firmware-reported maxima.

## Important APIs, Types, And Functions
Public functions are `bnge_aux_has_enough_resources`, `bnge_fix_rings_count`, `bnge_cal_nr_rss_ctxs`, `bnge_get_rxfh_indir_size`, `bnge_reserve_rings`, `bnge_alloc_irqs`, `bnge_free_irqs`, `bnge_net_init_dflt_config`, `bnge_net_uninit_dflt_config`, and `bnge_aux_init_dflt_config`. Internal helpers convert TX rings to completion demand, compute max/default rings, reserve auxiliary MSI-X/stat contexts, initialize RSS indirection, and trim shared rings.

## Control Flow
Default configuration allocates the RSS indirection table, computes default shared RX/TX/NQ counts from CPU/RSS defaults and firmware maxima, reserves rings through HWRM, and stores filter capacity. Before open, `bnge_reserve_rings` recalculates demand, asks firmware to reserve resources, copies actual reservations back, reduces local ring counts if necessary, updates NQ/stat counts, and refreshes RSS indirection when RX reservation changed. IRQ allocation then asks PCI for MSI-X vectors and readjusts ring counts to available vectors.

## State And Persistence
The file mutates `bd->rx_nr_rings`, `bd->tx_nr_rings`, `bd->tx_nr_rings_per_tc`, `bd->nq_nr_rings`, `bd->aux_num_msix`, `bd->aux_num_stat_ctxs`, `bd->irq_tbl`, `bd->irqs_acquired`, `bd->rss_indir_tbl`, and `bd->hw_resc` reservations. These values persist as the sizing basis for netdev allocation and firmware object creation.

## Dependencies And Integration Points
It depends on HWRM resource wrappers, PCI MSI-X allocation, ethtool RSS default helper, RoCE capability flags, and ring constants from `bnge_netdev.h` and `bnge_resc.h`.

## Risks
Resource math has many coupled dimensions. Shared-channel mode and multi-TC TX mapping can make TX rings and completion rings differ. RoCE reservations reduce L2 capacity. Unsigned arithmetic around available IRQs/stat contexts must avoid underflow when maxima are below current demand.

## Test Signals
Probe on systems with few and many MSI-X vectors, shared and non-shared channels, RoCE enabled/disabled, CPU-count variation, firmware resource reductions, and repeated reserve/open paths. Validate queue counts, RSS indirection size, and no open failure after reductions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_resc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_resc.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_resc.h

## Purpose
This header declares resource-accounting structures and APIs for `bnge`, including firmware resource limits/reservations, requested hardware ring counts, IRQ metadata, and helper constants for RoCE reservation.

## Important APIs, Types, And Functions
Important types are `struct bnge_hw_resc`, `struct bnge_hw_rings`, and `struct bnge_irq`. Public functions include `bnge_reserve_rings`, `bnge_fix_rings_count`, `bnge_alloc_irqs`, `bnge_free_irqs`, default config init/uninit helpers, auxiliary config init, RSS indirection sizing, RSS context count calculation, and `bnge_aux_has_enough_resources`. `bnge_adjust_pow_two` rounds page/block counts for ring sizing.

## Control Flow
The header supports the sequence: query firmware resource caps into `bnge_hw_resc`, compute desired `bnge_hw_rings`, reserve with firmware, allocate IRQ table/vectors, and initialize netdev default resource configuration.

## State And Persistence
`bnge_hw_resc` stores min/max/reserved counts for RSS contexts, completion/TX/RX rings, ring groups, L2 contexts, VNICs, stat contexts, NQs/MSI-X, and flow records. `bnge_irq` persists vector number, handler, request state, affinity mask state, and display name while IRQs are allocated.

## Dependencies And Integration Points
The header includes `bnge_netdev.h` and `bnge_rmem.h`, so it sits above ring data structures and below resource calculation. It is consumed by probe, netdev allocation, open, and HWRM reservation code.

## Risks
The inline rounding helper returns at least two blocks for zero or one input block, which is appropriate for ring/page-table sizing but would be surprising if reused for a different semantic. IRQ naming and affinity state require careful cleanup if request or affinity setup partially fails.

## Test Signals
Build coverage plus runtime checks of resource caps, queue counts, IRQ request/free, RSS table size, and RoCE auxiliary reservation. Low-resource firmware profiles should be included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_resc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_rmem.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_rmem.c

## Purpose
This file allocates and frees DMA ring memory and firmware backing-store context memory. It builds page tables for hardware rings, initializes context memory with firmware-requested values, configures backing store through HWRM, and initializes each netdev ring's `bnge_ring_mem_info` before allocation.

## Important APIs, Types, And Functions
Public functions are `bnge_alloc_ring`, `bnge_free_ring`, `bnge_alloc_ctx_mem`, `bnge_free_ctx_mem`, and `bnge_init_ring_struct`. Important internal helpers are `bnge_init_ctx_mem`, `bnge_alloc_ctx_one_lvl`, `bnge_alloc_ctx_pg_tbls`, `bnge_free_ctx_pg_tbls`, `bnge_setup_ctxm_pg_tbls`, and `bnge_backing_store_cfg`.

## Control Flow
Ring allocation optionally allocates a page-table DMA block, allocates each DMA page, writes valid/last PTE bits, optionally initializes context pages, and optionally allocates software virtual memory. Context allocation first queries qcaps, computes L2 plus optional RoCE QP/SRQ/CQ/TIM/TQM entries, allocates one- or two-level page tables, and sends backing-store config for all valid context types. Free paths walk the same nested page-table structures and release DMA/vmalloc/kzalloc memory.

## State And Persistence
`bnge_ring_mem_info` records page arrays, DMA arrays, page table, depth, flags, vmem pointer, and optional context type. `bd->ctx` holds `bnge_ctx_mem_info`, each valid `bnge_ctx_mem_type`, and allocated `bnge_ctx_pg_info` arrays. `BNGE_CTX_FLAG_INITED` marks that backing store was configured.

## Dependencies And Integration Points
It depends on HWRM backing-store qcaps/cfg wrappers, `bnge_netdev.h` ring page counts and descriptor sizes, `bnge_resc.h` sizing helper, Linux coherent DMA, vmalloc, and kdump/RoCE state.

## Risks
Partial allocation paths can leave nested context page tables requiring complete cleanup. Multi-level page-table construction uses fixed `MAX_CTX_PAGES` limits and must preserve firmware depth/page-size expectations. RoCE-enabled paths allocate much larger two-level contexts and are skipped in kdump.

## Test Signals
Open/close with normal L2, RoCE enabled, kdump kernel behavior, large firmware context requirements, and injected DMA allocation failures. Validate HWRM backing-store config success and no DMA leaks across repeated probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_rmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_rmem.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_rmem.h

## Purpose
This header defines the ring-memory and context-memory data structures used to allocate hardware-visible DMA rings and firmware backing-store pages for `bnge`.

## Important APIs, Types, And Functions
Important types are `struct bnge_ring_mem_info`, `struct bnge_ctx_pg_info`, `struct bnge_ctx_mem_type`, `struct bnge_ctx_mem_info`, and `struct bnge_ring_struct`. It defines PTE flags, hardware-supported page-size selection, context type aliases, backing-store constants, TQM limits, context initialization fields, and public APIs `bnge_alloc_ring`, `bnge_free_ring`, `bnge_alloc_ctx_mem`, `bnge_free_ctx_mem`, and `bnge_init_ring_struct`.

## Control Flow
The header underpins two flows. Descriptor rings fill `bnge_ring_mem_info` with page arrays and optional software vmem, then call `bnge_alloc_ring`. Firmware backing-store flow fills `bnge_ctx_mem_type` from qcaps, allocates `bnge_ctx_pg_info` page tables, and passes those to HWRM backing-store config.

## State And Persistence
Ring memory state tracks DMA page arrays, page-table DMA address, allocation depth, flags, and optional software memory. Context memory state tracks valid context types, entry sizes, instance bitmaps, initialization patterns, max/min entries, split entries, and allocated page-info arrays. `bnge_ring_struct` adds firmware ring ID, group/map index, handle, and queue ID.

## Dependencies And Integration Points
It relies on HSI backing-store type constants and is consumed by `bnge_rmem.c`, `bnge_netdev.c`, `bnge_hwrm_lib.c`, and `bnge_resc.c`. Page-size macros must remain compatible with RX descriptor length limits.

## Risks
Compile-time page-size selection changes ring geometry and maximum descriptor counts. Context type ranges (`BNGE_CTX_MAX`, `BNGE_CTX_L2_MAX`, `BNGE_CTX_V2_MAX`) must stay aligned with firmware HSI. `BNGE_SET_CTX_PAGE_ATTR` maps only supported page sizes and is reused by HWRM backing-store configuration.

## Test Signals
Build across page-size configurations, ring allocation with one and multiple pages, context qcaps/config on L2-only and RoCE-capable devices, and repeated allocation/free with fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_rmem.h -->
