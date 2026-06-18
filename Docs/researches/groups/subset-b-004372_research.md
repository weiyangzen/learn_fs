# subset-b-004372 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_sriov.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_sriov.c

## Purpose
Implements the PF-side SR-IOV control plane and the VF-side bulletin/PCI helpers for the Broadcom/QLogic `bnx2x` Ethernet driver. The file owns VF discovery from PCI SR-IOV capability and IGU CAM state, VF database setup, VF DMA allocation, VF queue/filter/multicast/RSS/TPA operations, FLR cleanup, per-VF netdev controls, PF/VF link and bulletin updates, VF PCI mailbox allocation on the VF side, and the delayed IOV work item that drains FLR and mailbox events.

## Important APIs, Types, and Functions
The exported PF lifecycle entry points are `bnx2x_iov_init_one`, `bnx2x_iov_alloc_mem`, `bnx2x_iov_nic_init`, `bnx2x_iov_init_ilt`, `bnx2x_enable_sriov`, `bnx2x_disable_sriov`, `bnx2x_sriov_configure`, `bnx2x_iov_chip_cleanup`, `bnx2x_iov_free_mem`, and `bnx2x_iov_remove_one`. VF lifecycle and resource APIs include `bnx2x_vf_acquire`, `bnx2x_vf_init`, `bnx2x_vf_close`, `bnx2x_vf_free`, `bnx2x_vf_release`, `bnx2x_vf_queue_setup`, `bnx2x_vf_queue_teardown`, `bnx2x_vf_mac_vlan_config_list`, `bnx2x_vf_mcast`, `bnx2x_vf_rxmode`, `bnx2x_vf_rss_update`, and `bnx2x_vf_tpa_update`.

Netdev/SR-IOV control hooks are `bnx2x_get_vf_config`, `bnx2x_set_vf_mac`, `bnx2x_set_vf_vlan`, `bnx2x_set_vf_spoofchk`, and `bnx2x_set_vf_link_state`. Event and integration helpers include `bnx2x_iov_eq_sp_event`, `bnx2x_iov_set_queue_sp_obj`, `bnx2x_iov_adjust_stats_req`, `bnx2x_vf_handle_flr_event`, `bnx2x_vf_enable_mbx`, `bnx2x_post_vf_bulletin`, `bnx2x_sample_bulletin`, `bnx2x_timer_sriov`, `bnx2x_iov_channel_down`, `bnx2x_iov_task`, and `bnx2x_schedule_iov_task`.

## Control Flow and State
Probe-time setup starts in `bnx2x_iov_init_one`: it rejects VFs, E1x chips, disabled SR-IOV, PF CID overlap, MSI/INTx, missing ARI, and IGU backward-compatible mode; allocates `bp->vfdb`; reads PCI SR-IOV config and device first-VF information; creates `struct bnx2x_virtf` records; reads IGU CAM SB ownership; allocates the global VF queue array; and initializes event/bulletin mutexes. `bnx2x_iov_alloc_mem` then allocates VF CDU contexts, slowpath ramrod DMA, mailbox DMA, and bulletin DMA. `bnx2x_iov_nic_init` initializes static per-VF resource credits, multicast objects, mailbox pointers, mailbox enablement, BDF identity, and BAR slices.

Runtime enablement in `bnx2x_enable_sriov` partitions the VF status-block pool across requested VFs, rewrites IGU mapping memory, binds each VF to its slice of the shared VF queue array, programs VF MSI-X table size through pretend mode, enables PF Tx switching, and calls `pci_enable_sriov`. Disable uses `pci_disable_sriov` unless VFs are assigned. Remove additionally disables internal access for all possible VFs and frees `bp->vfdb`.

VF resource state is centered on `struct bnx2x_virtf::state`: `VF_FREE`, `VF_ACQUIRED`, `VF_ENABLED`, `VF_RESET`, and `VF_LOST`. `bnx2x_vf_acquire` validates requested resources against static credits and initializes per-queue context pointers/CIDs and queue SP objects. `bnx2x_vf_init` initializes VF status blocks, verifies FLR completion, calls function init, enables SEMI/PGLUE/PBF/IGU access, updates the host-zone permission table, marks `VF_ENABLED`, and posts the bulletin. `bnx2x_vf_close` tears down queues, disables IGU and queue table access, then uses `bnx2x_stats_safe_exec` to move the VF back to `VF_ACQUIRED` only after outstanding stats ramrods are drained.

FLR handling reads MCP disabled-VF bits from shared memory, marks matching VFs as `VF_RESET`, serializes each cleanup under the VF/PF channel mutex, clears queue/filter/mcast state, sends final cleanup, polls DORQ and TX flush, resets VF resource counters, reopens the mailbox, and ACKs the MCP bits. The code deliberately ACKs all bits reported by MCP to avoid interrupt loops from hypervisors that report unopened VFs.

## State and Persistence Behavior
Persistent driver state lives in `bp->vfdb`, `bp->vfdb->vfs`, `bp->vfdb->vfqs`, per-VF `alloc_resc`, VF queue state objects, filter credit pools, mailbox/event bitmaps, and local PF copies of bulletin contents. Hardware-visible state is programmed into IGU mapping/configuration, DORQ VF CID/doorbell registers, PGLUE internal VF enable/error registers, PBF VF disable, PXP host-zone permission table, SEMI storm memories, MCP shared memory, PCI SR-IOV config space, and VF DMA-visible mailbox/bulletin buffers. Bulletin contents use a monotonically incremented version plus CRC and can be long or legacy-sized depending on VF capability.

## Dependencies and Integration Points
Depends on `bnx2x.h`, `bnx2x_init.h`, `bnx2x_cmn.h`, `bnx2x_sp.h`, `bnx2x_sriov.h`, `bnx2x_vfpf.h`, PCI SR-IOV/ARI APIs, Linux netdev VF ndo hooks, workqueues, MCP shared memory, DMAE, IGU, DORQ, PGLUE, PBF, SEMI storm memory, queue state ramrods, VLAN/MAC/multicast/RSS objects, and the stats subsystem. It is invoked from main probe/load/unload paths, event-ring handling, timer paths, VF-PF mailbox code, and netdev operations.

## Risks and Test Signals
Main risks are off-by-one VF and queue bounds, IGU CAM redistribution mistakes, stale VF state after failed acquire/init/close, deadlocks or mismatched `op_mutex` TLV ownership, FLR cleanup racing with mailbox/filter operations, DMAE copies to guest-provided bulletin/stat addresses, mailbox reopening before final cleanup is complete, and stats ramrods accessing freed VF buffers. Policy risks include host-set MAC/VLAN enforcement, spoof-check updates only for active queues, `pci_vfs_assigned` preventing disable, and forced ACK of all MCP FLR bits.

Good test signals include enabling/disabling SR-IOV through sysfs, VF probe/acquire/init/queue setup/teardown/release, VF FLR while traffic and filters are active, assigned-VF unload behavior, host `ip link set dev ... vf ... mac/vlan/spoofchk/link-state`, guest bulletin CRC/version/link updates, multicast/RSS/TPA VF requests, event-ring completions for VF CFC/filter/mcast/RSS/malicious events, and stats collection with enabled, disabled, and malicious VFs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_sriov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_sriov.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_sriov.h

## Purpose
Defines the SR-IOV data model and build-time interface for the `bnx2x` driver. It describes PF-owned VF records, per-VF queues, mailbox/bulletin DMA layout, resource counters, state constants, TLV channel locking, and all PF and VF SR-IOV function prototypes. When `CONFIG_BNX2X_SRIOV` is disabled, it supplies stubs that let the rest of the driver compile and behave as non-SR-IOV.

## Important APIs, Types, and Functions
Key types are `struct bnx2x_sriov` for PCI SR-IOV capability metadata, `struct bnx2x_vf_bar`, `struct bnx2x_vf_queue`, `struct bnx2x_vf_queue_construct_params`, `struct bnx2x_vf_mac_vlan_filter`, `struct bnx2x_vf_mac_vlan_filters`, `struct bnx2x_virtf`, `struct bnx2x_vf_mbx_msg`, `struct bnx2x_vf_mbx`, `struct bnx2x_vf_sp`, `struct hw_dma`, and `struct bnx2x_vfdb`. Inline helpers map VF queues and IDs, including `vfq_get`, `vf_igu_sb`, `vf_hc_qzone`, `vfq_cl_id`, `vfq_stat_id`, and `vfq_qzone_id`.

Important macros include `BNX2X_VF_MAX_QUEUES`, `BNX2X_VF_MAX_TPA_AGG_QUEUES`, VF states (`VF_FREE`, `VF_ACQUIRED`, `VF_ENABLED`, `VF_RESET`, `VF_LOST`), VF config flags (`VF_CFG_STATS_COALESCE`, `VF_CFG_EXT_BULLETIN`, `VF_CFG_VLAN_FILTER`), resource accessors (`vf_rxq_count`, `vf_txq_count`, `vf_sb_count`, `vf_mac_rules_cnt`, `vf_vlan_rules_cnt`, `vf_mc_rules_cnt`), iteration helpers (`for_each_vf`, `for_each_vfq`, `for_each_vf_sb`), and handle conversion macros (`HW_VF_HANDLE`, `FW_VF_HANDLE`). The declared functions span IOV setup/teardown, mailbox handling, queue/filter/mcast/RSS/TPA operations, FLR cleanup, bulletin handling, VF-side VF-PF requests, and netdev VF controls.

## Control Flow and State
The header has little runtime flow beyond inline ID mapping and build-time stub dispatch. Its state model is central: `struct bnx2x_vfdb` hangs from `bp->vfdb` and owns the VF array, global VF queue array, context pages, SR-IOV PCI metadata, mailbox array, bulletin DMA, slowpath DMA, FLR bitmaps, event mutex/state, and bulletin mutex. Each `struct bnx2x_virtf` tracks lifecycle state, FLR/malicious flags, spoof check, stat/bulletin DMA addresses, resource counters, IGU base, queue pointer, BDF/BAR identity, filtering state, leading RSS client, multicast/RSS objects, per-VF operation mutex/current TLV, fastpath HSI version, and credit pools.

## State and Persistence Behavior
The declarations encode which state persists in software across operations and which state mirrors hardware/guest-visible resources. VF queue state persists in `struct bnx2x_vf_queue` objects and associated slowpath objects. Mailbox and bulletin persistence is represented by DMA-backed `struct hw_dma` regions and per-VF guest physical addresses. Compile-time stubs convert SR-IOV resource counts to zero and make SR-IOV actions no-ops when support is not built.

## Dependencies and Integration Points
Includes `bnx2x_vfpf.h` for TLV and bulletin structures and `bnx2x.h` for core driver types. The header is consumed by `bnx2x_sriov.c`, `bnx2x_vfpf.c`, `bnx2x_stats.c`, main event/timer/probe paths, netdev ndo declarations, and queue/filter/RSS/multicast code. Its stubs are important integration points for non-SR-IOV builds.

## Risks and Test Signals
Risks are ABI-like: wrong handle conversion, resource counter semantics, queue indexing, mailbox alignment, or stub behavior can break PF/VF communication or non-SR-IOV builds. The pointer arithmetic macros for `bnx2x_vf_sp` and mailbox/bulletin DMA require matching allocation sizes. Test signals include allmodconfig and `CONFIG_BNX2X_SRIOV=n` builds, VF acquire/init with maximum queues, FLR paths using initialized and uninitialized VF objects, stats coalescing mode, long and legacy bulletin support, and code paths that include this header without SR-IOV enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_sriov.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_stats.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_stats.c

## Purpose
Implements the `bnx2x` statistics engine. It initializes DMA-backed statistics buffers, builds firmware statistics ramrod requests, posts DMAE and storm statistics queries, validates firmware completion counters, folds hardware/firmware/driver counters into `bp->eth_stats`, updates `net_device_stats`, preserves counters across unload/reset, and offers a safe execution gate for operations that must not race with outstanding stats.

## Important APIs, Types, and Functions
Public entry points are `bnx2x_memset_stats`, `bnx2x_stats_init`, `bnx2x_stats_handle`, `bnx2x_save_statistics`, `bnx2x_afex_collect_stats`, and `bnx2x_stats_safe_exec`. Important internal functions include `bnx2x_get_port_stats_dma_len`, `bnx2x_storm_stats_post`, `bnx2x_hw_stats_post`, `bnx2x_stats_comp`, `bnx2x_stats_pmf_update`, `bnx2x_port_stats_init`, `bnx2x_func_stats_init`, `bnx2x_stats_start`, `bnx2x_stats_pmf_start`, `bnx2x_stats_restart`, `bnx2x_hw_stats_update`, `bnx2x_storm_stats_validate_counters`, `bnx2x_storm_stats_update`, `bnx2x_net_stats_update`, `bnx2x_drv_stats_update`, `bnx2x_stats_update`, `bnx2x_port_stats_stop`, `bnx2x_stats_stop`, `bnx2x_port_stats_base_init`, and `bnx2x_prep_fw_stats_req`.

## Control Flow and State
Statistics are driven by a two-state finite-state machine `bnx2x_stats_stm`, keyed by `STATS_STATE_DISABLED`/`STATS_STATE_ENABLED` and events `STATS_EVENT_PMF`, `STATS_EVENT_LINK_UP`, `STATS_EVENT_UPDATE`, and `STATS_EVENT_STOP`. `bnx2x_stats_handle` serializes transitions with `bp->stats_lock`; timer updates return immediately on contention while non-timer events wait briefly.

`bnx2x_stats_init` reads management shared-memory addresses for port/function statistics, handles PMF migration, seeds old NIG counters, prepares the firmware stats query list, optionally clears host function stats, and calls `bnx2x_memset_stats`. `bnx2x_prep_fw_stats_req` lays out port, PF, optional FCoE, and queue query entries; each storm stats post lets `bnx2x_iov_adjust_stats_req` append enabled non-malicious VF queue stats.

On update, PFs first require DMAE completion, update hardware MAC/NIG counters if PMF, validate storm counters for the last stats ramrod, fold per-queue tstorm/ustorm/xstorm counters into queue, function, and Ethernet totals, then post the next hardware and storm requests. VFs skip hardware stats and completion handling, using only storm stats updates. Stop drains DMAE, does a final update, copies final port/function stats to MCP memory, posts DMAE, and waits for completion.

## State and Persistence Behavior
Persistent software counters live in `bp->eth_stats`, `bp->func_stats`, `bp->dev->stats`, `bp->fp_stats[*].eth_q_stats`, and the corresponding `_old` snapshots used to preserve or delta counters across firmware reset/unload. Hardware and firmware snapshots live in slowpath DMA memory (`port_stats`, `func_stats`, `mac_stats`, `nig_stats`, `fw_stats_req`, `fw_stats_data`, `stats_comp`). `bp->stats_counter` sequences storm ramrods, `bp->stats_pending` tracks outstanding storm updates and triggers a panic after repeated missed updates, and `bp->stats_init` controls whether full counters are reset or old values are preserved.

## Dependencies and Integration Points
Depends on `bnx2x_stats.h` macros and structures, `bnx2x_cmn.h`, `bnx2x_sriov.h`, DMAE helpers, storm firmware statistics layouts, MCP shared memory, link MAC type selection, queue/fastpath iteration macros, FCoE/VIC AFEX structures, and SR-IOV stats query adjustment. Callers include link-up/link-down and PMF paths, the periodic timer, ethtool test paths that stop stats, unload paths that call `bnx2x_save_statistics`, and VF close code that uses `bnx2x_stats_safe_exec`.

## Risks and Test Signals
Risks include DMA length miscalculation from management firmware size fields, counter wrap/delta errors in macro-heavy update code, missing storm completions causing stale stats or panic, PMF migration copying stale port stats, stats DMA racing with VF teardown, FCoE query index shifts, and different MAC type register layouts. Test signals include link-up stats start, periodic stats updates, link flap/restart, PMF handoff, unload/reload counter preservation, VF stats with enabled/malicious/closed VFs, FCoE and non-FCoE builds, EMAC/BMAC/UMAC/XMAC hardware, ethtool stats/register tests, and forced storm timeout or DMAE completion timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_stats.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_stats.h

## Purpose
Declares the `bnx2x` statistics state machine events/states, persistent Ethernet statistics structures, old-counter snapshots, NIG stats layout, arithmetic/update macros, and exported statistics APIs. It is the contract used by the stats implementation, core driver paths, ethtool, and SR-IOV teardown synchronization.

## Important APIs, Types, and Functions
Important types are `struct nig_stats`, `enum bnx2x_stats_event`, `enum bnx2x_stats_state`, `struct bnx2x_eth_stats`, `struct bnx2x_eth_q_stats`, `struct bnx2x_eth_stats_old`, `struct bnx2x_eth_q_stats_old`, `struct bnx2x_net_stats_old`, and `struct bnx2x_fw_port_stats_old`. Exported functions are `bnx2x_memset_stats`, `bnx2x_stats_init`, `bnx2x_stats_handle`, `bnx2x_stats_safe_exec`, `bnx2x_save_statistics`, and `bnx2x_afex_collect_stats`.

The macro layer performs 64-bit split-counter arithmetic and counter folding: `ADD_64`, `ADD_64_LE`, `ADD_64_LE16`, `DIFF_64`, `UPDATE_STAT64`, `UPDATE_STAT64_NIG`, `ADD_EXTEND_64`, `ADD_STAT64`, `UPDATE_EXTEND_STAT`, `UPDATE_EXTEND_TSTAT`, `UPDATE_EXTEND_E_TSTAT`, `UPDATE_EXTEND_USTAT`, `UPDATE_EXTEND_E_USTAT`, `UPDATE_EXTEND_XSTAT`, `UPDATE_QSTAT`, `UPDATE_QSTAT_OLD`, `UPDATE_ESTAT_QSTAT_64`, `UPDATE_ESTAT_QSTAT`, `UPDATE_FSTAT_QSTAT`, `UPDATE_FW_STAT`, `UPDATE_FW_STAT_OLD`, `UPDATE_ESTAT`, `SUB_64`, `SUB_EXTEND_64`, and `SUB_EXTEND_USTAT`.

## Control Flow and State
This header has no standalone runtime control flow, but it defines the events and states consumed by `bnx2x_stats_handle`. The structures distinguish total Ethernet counters, per-queue counters, and "old" snapshots used to compute deltas or preserve values over reset/unload. Many fields are split high/low 32-bit values because hardware and firmware counters are exposed as 32-bit words or little-endian split values.

## State and Persistence Behavior
`struct bnx2x_eth_stats` is the long-lived aggregate exported to netdev and ethtool-style consumers. `struct bnx2x_eth_q_stats` tracks per-fastpath queue totals. The `_old` structures intentionally persist selected values across firmware reset or unload, and the macros update those snapshots as deltas are consumed. `struct bnx2x_fw_port_stats_old` preserves MF firmware port discard counters for PMF-owned port stats.

## Dependencies and Integration Points
Includes Linux integer types and forward-declares `struct bnx2x`. It is included by `bnx2x_stats.c` and other driver modules that emit stats events, save statistics, or use safe stats execution. The field names and macro assumptions are tightly coupled to firmware statistics structures in the broader `bnx2x` HSI headers and to the slowpath layout used by DMAE.

## Risks and Test Signals
Risks are mostly structural and arithmetic: field-order changes can break `struct_group` copies, macro call sites depend on local variable names such as `new`, `old`, `pstats`, `estats`, `qstats`, and `diff`, and split-counter arithmetic must handle wrap without negative totals. Test signals include compile coverage for all macro call sites, sparse/endian checks for little-endian macros, stats continuity across reset/unload, 32-bit and 64-bit architecture builds, and ethtool/netdev stat comparisons under traffic, drops, TPA, pause/PFC, and FCoE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_vfpf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_vfpf.c

## Purpose
Implements the VF-PF mailbox protocol for `bnx2x`. The first half builds and sends VF-side TLV requests to the PF for acquire, release, init, close, queue setup/teardown, MAC/VLAN/multicast/RX-mode filters, RSS, and VLAN updates. The second half is the PF-side mailbox engine: it DMAE-copies VF requests from guest memory, validates and dispatches TLVs, executes PF-side VF operations from `bnx2x_sriov.c`, and DMAE-copies responses and bulletins back to the VF.

## Important APIs, Types, and Functions
VF-side public functions are `bnx2x_vfpf_acquire`, `bnx2x_vfpf_release`, `bnx2x_vfpf_init`, `bnx2x_vfpf_close_vf`, `bnx2x_vfpf_setup_q`, `bnx2x_vfpf_config_mac`, `bnx2x_vfpf_config_rss`, `bnx2x_vfpf_set_mcast`, `bnx2x_vfpf_update_vlan`, and `bnx2x_vfpf_storm_rx_mode`. Common TLV helpers include `bnx2x_add_tlv`, `bnx2x_vfpf_prep`, `bnx2x_vfpf_finalize`, `bnx2x_search_tlv_list`, `bnx2x_dp_tlv_list`, `bnx2x_tlv_supported`, `bnx2x_pfvf_status_codes`, `bnx2x_send_msg2pf`, and `bnx2x_get_vf_id`.

PF-side mailbox functions include `bnx2x_vf_enable_mbx`, `bnx2x_copy32_vf_dmae`, `bnx2x_vf_mbx_resp_single_tlv`, `bnx2x_vf_mbx_resp_send_msg`, `bnx2x_vf_mbx_acquire_resp`, `bnx2x_vf_mbx_acquire`, `bnx2x_vf_mbx_init_vf`, `bnx2x_vf_mbx_setup_q`, `bnx2x_vf_mbx_qfilters`, `bnx2x_vf_mbx_set_q_filters`, `bnx2x_vf_mbx_teardown_q`, `bnx2x_vf_mbx_close_vf`, `bnx2x_vf_mbx_release_vf`, `bnx2x_vf_mbx_update_rss`, `bnx2x_vf_mbx_update_tpa`, `bnx2x_vf_mbx_request`, `bnx2x_vf_mbx_schedule`, `bnx2x_vf_mbx`, `bnx2x_vf_bulletin_finalize`, and `bnx2x_post_vf_bulletin`.

## Control Flow and State
VF-side request flow always locks `bp->vf2pf_mutex`, clears the shared mailbox, writes a first TLV with response offset, appends optional TLVs and a list terminator, writes the mailbox DMA address into the VF/PF channel, triggers firmware, waits up to roughly 10 seconds for PF status, interprets PFVF status, and unlocks. Acquire first reads the VF ID through the ME register trap, requests resources and a bulletin address, advertises extended bulletin and VLAN-filter support, retries with PF-recommended smaller resources on `NO_RESOURCE`, then stores PF device info, queue/SB resources, FW version, physical port ID, and MAC into `bp`.

PF-side event flow starts when `bnx2x_vf_mbx_schedule` records a VF guest mailbox address and sets an event bit. `bnx2x_vf_mbx` drains event bits, DMAE-copies the VF request into PF-owned mailbox memory, stores the first TLV header, clears the response buffer, and dispatches through `bnx2x_vf_mbx_request`. Supported TLVs are serialized under the per-VF channel mutex and call the matching SR-IOV operations. Responses are prepared as TLVs, status is mapped from errno, the response body is copied first, firmware is ACKed, then the first 64 bits containing the done/status header are copied last so the VF sees a coherent completion.

Filter control validates host policy before applying VF requests. If a host-set MAC exists in the bulletin, the VF may configure only that MAC and only one MAC. If a host-set VLAN exists, VF VLAN filter requests are rejected and RX any-VLAN acceptance is suppressed. RSS validates table/key sizes and blocks UDP-only modes that would hit firmware assertions. TPA validates SGE and aggregation limits before queue update ramrods.

## State and Persistence Behavior
VF-side persistent protocol state lives in `bp->vf2pf_mbox`, `bp->vf2pf_mbox_mapping`, `bp->pf2vf_bulletin`, `bp->old_bulletin`, `bp->shadow_bulletin`, `bp->acquire_resp`, and the VF netdev/link fields updated from bulletins. PF-side state lives in `BP_VF_MBX(bp, vf)->msg`, `msg_mapping`, saved guest address, saved first TLV, per-VF resource/stat/bulletin fields, and `bp->vfdb->event_occur`. Bulletins are versioned and CRC-protected, with the length set for long or legacy VF support.

## Dependencies and Integration Points
Depends on TLV structures and constants from `bnx2x_vfpf.h`, SR-IOV state and operations from `bnx2x_sriov.h`, core queue/filter/RSS/mcast functions, DMAE, storm mailbox-valid/ack memory, VF doorbell/ME register behavior, netdev multicast lists, bulletin CRC helpers, and PF firmware event delivery through `bnx2x_main.c`. It also integrates with guest-visible netdev setup paths because VF open/close and filter changes are routed through these VF-side request builders.

## Risks and Test Signals
Major risks include malformed TLV lists, zero-length TLVs, stale response status causing false completions, PF timeout handling, guest-provided DMA addresses, response ordering around the done/status header, mailbox lock mismatches, unsupported future TLVs, off-by-one VF ID validation, filter policy bypass, and firmware assertions from invalid RSS/TPA inputs. Test signals include VF acquire retry with reduced resources, old hypervisor/old VF compatibility paths, channel-down bulletins, PF timeout, queue setup/teardown, host-forced MAC/VLAN with guest attempts to override, multicast list size limits, RSS and TPA update validation, malicious/lost VF behavior, FLR during mailbox activity, and CRC/version validation for bulletins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnx2x/bnx2x_vfpf.c -->
