# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_main.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004458`: lines 1-9299, `Docs/researches/chunks/subset-b-004458_research.md`
- `subset-b-004459`: lines 9300-16679, `Docs/researches/chunks/subset-b-004459_research.md`

## Chunk Research

### subset-b-004458: lines 1-9299

# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_main.c lines 1-9299

## Scope and Purpose

This chunk is the front half of Intel's `i40e_main.c` PF driver for XL710/X710/XXV710-era Ethernet controllers. It begins with module identity, PCI device IDs, memory helpers used by shared hardware code, generic PF/VSI resource allocation helpers, statistics collection, MAC/VLAN filter management, RSS and queue mapping, descriptor-ring setup, interrupt setup, queue start/stop, DCB and mqprio/channel support, macvlan offload, TC flower cloud filters, and netdev open/close plus the beginning of reset dispatch.

The code in this range is not merely plumbing. It is the runtime center for bringing a VSI from software configuration into programmed hardware state: filters are accumulated in driver hash tables, queue mappings are written through AdminQ contexts, descriptor rings are programmed into HMC contexts, interrupts are requested and linked to queues, NAPI is enabled, and link/carrier state is exposed to the network stack. Later chunks continue reset, probe, remove, and module lifecycle details.

## Important APIs, Types, and Data

Key state objects visible in this chunk:

- `struct i40e_pf`: adapter/PF-wide state. This chunk updates `state`, `flags`, `hw`, `pdev`, `vsi[]`, `qp_pile`, `irq_pile`, `msix_entries`, statistics, reset counters, Flow Director counters/lists, cloud filter list, DCB/RSS capabilities, timeout recovery counters, service work, and link-related flags.
- `struct i40e_vsi`: virtual station interface state. Important fields here include `type`, `seid`, `id`, `back`, `netdev`, `base_queue`, `base_vector`, `num_queue_pairs`, `alloc_queue_pairs`, `num_q_vectors`, `tx_rings`, `rx_rings`, `xdp_rings`, `q_vectors`, `mac_filter_hash`, `mac_filter_hash_lock`, `active_vlans`, `state`, `flags`, `info`, `tc_config`, RSS user/default data, channel/macvlan lists, and queue-channel counters.
- `struct i40e_ring` and `struct i40e_q_vector`: descriptor-ring and interrupt/NAPI units. This chunk binds rings to q_vectors, programs HMC queue contexts, stores MMIO tail pointers, configures XPS, AF_XDP pools, XDP RX queue metadata, and ITR state.
- `struct i40e_mac_filter` and `struct i40e_new_mac_filter`: software MAC/VLAN filter records. Filters transition among `I40E_FILTER_NEW`, `I40E_FILTER_NEW_SYNC`, `I40E_FILTER_ACTIVE`, `I40E_FILTER_FAILED`, and `I40E_FILTER_REMOVE`.
- `struct i40e_channel`, `struct i40e_fwd_adapter`, and `struct i40e_cloud_filter`: auxiliary state for mqprio channel VSIs, macvlan L2 forwarding offload, and TC flower/cloud-filter offload.
- AdminQ/HMC descriptor structs: VSI contexts, MAC/VLAN add/remove element data, cloud-filter element data, queue contexts, DCB BW configuration structures, and PHY configuration data are populated locally then submitted through `i40e_aq_*` or HMC helper APIs.

Important entry points and callback-visible functions in this chunk:

- Module/PF basics: `i40e_hw_to_dev()`, `i40e_allocate_dma_mem()`, `i40e_free_dma_mem()`, `i40e_allocate_virt_mem()`, `i40e_free_virt_mem()`, `i40e_find_vsi_from_id()`, `i40e_service_event_schedule()`.
- Stats: `i40e_get_vsi_stats_struct()`, `i40e_vsi_reset_stats()`, `i40e_pf_reset_stats()`, `i40e_update_eth_stats()`, `i40e_update_veb_stats()`, `i40e_update_stats()`.
- MAC/VLAN filters: `i40e_add_filter()`, `__i40e_del_filter()`, `i40e_add_mac_filter()`, `i40e_del_mac_filter()`, `i40e_set_mac()`, `i40e_set_rx_mode()`, `i40e_sync_vsi_filters()`, `i40e_sync_filters_subtask()`, VLAN add/delete/restore/PVID helpers.
- Queue/RSS/ring setup: `i40e_vsi_config_rss()`, `i40e_vsi_setup_queue_map()`, `i40e_configure_tx_ring()`, `i40e_configure_rx_ring()`, `i40e_vsi_configure()`.
- Interrupts and queues: `i40e_vsi_configure_msix()`, `i40e_intr()`, `i40e_msix_clean_rings()`, `i40e_vsi_request_irq()`, `i40e_vsi_free_irq()`, `i40e_vsi_start_rings()`, `i40e_vsi_stop_rings()`, `i40e_vsi_wait_queues_disabled()`.
- Traffic class and channel support: DCB helpers under `CONFIG_I40E_DCB`, `i40e_vsi_config_tc()`, `i40e_set_bw_limit()`, `i40e_create_queue_channel()`, `i40e_configure_queue_channels()`, `i40e_setup_tc()`.
- Offloads: macvlan offload via `i40e_fwd_add()`/`i40e_fwd_del()`, TC flower offload via `i40e_parse_cls_flower()`, `i40e_configure_clsflower()`, and `i40e_delete_clsflower()`.
- Netdev lifecycle: `i40e_open()`, `i40e_vsi_open()`, `i40e_up()`, `i40e_down()`, `i40e_close()`, and the beginning of `i40e_do_reset()`.

## Initialization and Resource Allocation

The file starts by declaring the driver name/string, PCI device table, debug module parameter, imported namespaces, and a global workqueue pointer. The PCI table covers XL710/X710/X722/N3000/25G variants, with a special Ethernet-class match for a device ID that conflicts with `ipw2200`.

`i40e_allocate_dma_mem()` and `i40e_allocate_virt_mem()` are OS adapters for shared hardware code. DMA memory is coherent, aligned to the requested boundary, and owned by `pf->pdev->dev`; virtual memory is zeroed with `kzalloc`. The matching free helpers null and zero the tracked pointers/sizes so shared-code callers do not retain stale memory metadata.

`i40e_get_lump()` and `i40e_put_lump()` implement contiguous allocation from generic PF resource piles such as queue pairs and IRQ vectors. The allocation bitmap/list stores `id | I40E_PILE_VALID_BIT`. A special case reserves the last queue for the Flow Director VSI to avoid fragmenting the normal queue pile. This allocator is an important hidden dependency for queue/vector setup and reset rebuild.

`i40e_service_event_schedule()` gates service task scheduling on PF state: normal service is queued when the PF is not down and reset recovery is not pending, while recovery mode is allowed to schedule service even with different down-state semantics.

## Statistics Behavior

Stats collection has three layers:

- Per-ring packet/byte counters are accumulated with `u64_stats_fetch_begin()`/retry under RCU-safe ring pointer reads.
- VSI Ethernet counters are read from GLV registers through 32-bit, 48-bit, or 64-bit helpers and normalized against first-read offsets because hardware counters are not reset by PF reset.
- PF and VEB counters pull port, switch, flow-control, packet-size, FDIR, EEE, and per-TC values from hardware registers.

`i40e_update_vsi_stats()` skips when the VSI is down or the PF is configuration-busy, sums Tx/Rx/XDP ring data, updates driver-maintained failure/reuse counters, then calls `i40e_update_eth_stats()` and maps hardware stats into netdev-visible fields. The main VSI also exposes selected PF port errors as netdev receive errors.

`i40e_update_pf_stats()` updates port-global counters and reads-and-clears Flow Director match counters. It also sets `fd_sb_status` and `fd_atr_status` based on feature flags and auto-disable state. Reset helpers clear both statistics and offset-loaded booleans, forcing the next update to establish fresh baselines.

Test and maintenance risk: these paths depend on correct offset handling across PF reset, counter wrap, QEMU's split 48-bit path, and concurrent ring teardown. The ring reads use RCU and `READ_ONCE`, but callers must still avoid invalidating ring arrays without the expected synchronization.

## MAC, VLAN, and Promiscuous Filter State Machine

The MAC/VLAN filter path is one of the densest state machines in this chunk. Software truth lives in `vsi->mac_filter_hash`, protected by `mac_filter_hash_lock`. Public add/delete helpers only change software state, set `I40E_VSI_FLAG_FILTER_CHANGED`, and set `__I40E_MACVLAN_SYNC_PENDING`; actual firmware programming is deferred to the service task via `i40e_sync_vsi_filters()`.

`i40e_add_filter()` deduplicates by MAC/VLAN, allocates a new record for missing filters, marks VLAN mode if `vlan >= 0`, and revives a `REMOVE` filter back to `ACTIVE` if an add races before the sync pass. `__i40e_del_filter()` immediately frees filters that never reached firmware (`NEW` or `FAILED`) and otherwise marks them for removal.

VLAN mode correction is explicit:

- Without active VLANs, non-PVID filters use `I40E_VLAN_ANY` so tagged and untagged traffic can match.
- With active VLANs, non-VLAN filters are rewritten to VLAN 0 so they match untagged traffic only.
- With a PVID, filters are rewritten to the PVID.
- VF filters are further adjusted by trust and the `I40E_FLAG_VF_VLAN_PRUNING_ENA` flag.

`i40e_sync_vsi_filters()` serializes itself with `__I40E_VSI_SYNCING_FILTERS`, builds temporary add/delete lists under the spinlock, corrects VLAN semantics, then releases the lock for AdminQ calls. Deletes use `i40e_aq_remove_macvlan_v2()` and ignore firmware `ENOENT`; adds use `i40e_aq_add_macvlan_v2()` and infer per-filter success from firmware-updated `match_method`. Broadcast filters are handled through VSI broadcast-promiscuous AdminQ commands rather than normal MAC filter commands.

Overflow handling is also stateful. If firmware cannot add filters, the main VSI enters `__I40E_VSI_OVERFLOW_PROMISC`; a threshold is recorded so the driver can leave overflow promiscuous once failed filters are gone and active filters drop below three quarters of the entry count at overflow entry. Untrusted SR-IOV VSIs are prevented from using this promiscuous fallback.

Promiscuous mode is programmed either as default-VSI behavior on the main VSI when a main VEB exists and MFP is disabled, or as unicast/multicast promiscuous flags on the VSI. `IFF_ALLMULTI`, `IFF_PROMISC`, and overflow-promisc transitions are reconciled during filter sync.

Risks in this area include rollback correctness on allocation failure, refcount adjustment through `netdev_hw_addr_refcnt()`, software/hardware divergence after partial AdminQ failure, and assumptions that all callers hold `mac_filter_hash_lock` where required by helper comments and `lockdep_assert_held()`.

## MTU, VLAN Offload, and PVID Handling

`i40e_change_mtu()` computes the maximum allowed MTU from the active XDP program and receive buffer model. Non-fragment XDP programs limit the chain length to one buffer, while normal/frags-capable paths use the hardware chain limit. A running netdev is reinitialized under `__I40E_CONFIG_BUSY` through `i40e_vsi_reinit_locked()`, which calls `i40e_down()` then `i40e_up()`.

VLAN stripping helpers update the VSI VLAN valid section through `i40e_aq_update_vsi_params()`, unless a PVID is active. `i40e_vsi_add_vlan()` ignores VID 0 because the hardware receives priority-tagged traffic with untagged traffic and a VID 0 hardware filter would incorrectly suppress untagged frames. Active VLANs are remembered in `vsi->active_vlans`; `i40e_restore_vlan()` reapplies strip state and re-marks active VLAN bits during up/rebuild paths.

`i40e_vsi_add_pvid()` programs a port VLAN insertion/stripping mode through the VSI context, while `i40e_vsi_remove_pvid()` clears `info.pvid` and returns VLAN stripping to normal disabled behavior. PVID changes interact directly with the MAC/VLAN correction logic described above.

## RSS and Queue Mapping

RSS setup uses AdminQ when `I40E_HW_CAP_RSS_AQ` is set. `i40e_vsi_config_rss()` chooses a user-provided LUT/hash key if present; otherwise it fills a default LUT and random netdev RSS key. RSS size defaults to the smaller of PF allocated RSS capacity and VSI queue pairs. Later channel and mqprio paths may reprogram RSS for non-power-of-two or reduced queue layouts.

`i40e_vsi_setup_queue_map()` translates enabled traffic classes into a VSI context queue map. The main VSI takes its queue count from requested channels, MSI-X LAN vectors, or one queue in non-MSI-X mode. DCB divides queue pairs across enabled TCs, capped by `i40e_pf_get_max_q_per_tc()` and MSI-X vectors. The function fills `tc_config`, AQ TC mappings, queue offset/count information, and contiguous or non-contiguous queue mapping based on VSI type.

`i40e_vsi_setup_queue_map_mqprio()` is the hardware mqprio-specific path for the main VSI. It uses the user-supplied offsets/counts, reconfigures RSS to the maximum queue count among TCs, records that RSS must later be restored/reconfigured, and sets aside queue ranges for channel VSIs.

## Ring Configuration and XDP/AF_XDP Integration

Tx and Rx descriptor memory is allocated per ring through `i40e_setup_tx_descriptors()` and `i40e_setup_rx_descriptors()`; XDP Tx rings are allocated/configured when `i40e_enabled_xdp_vsi()` is true.

`i40e_configure_tx_ring()` programs HMC Tx context fields: descriptor base, queue length, Flow Director enable, PTP timestamp enable, head writeback, scheduler ready-list handle, and queue ownership in `QTX_CTL`. It clears the old LAN Tx context before setting the new one, programs PF/VM ownership based on VSI/channel type, flushes, and caches the MMIO tail pointer.

`i40e_configure_rx_ring()` registers XDP RX queue info for main VSIs, selects either AF_XDP zero-copy or page-shared memory model, initializes the XDP buffer, programs HMC Rx context fields, configures build_skb alignment, caches and clears the Rx tail register, and preallocates receive buffers. AF_XDP rings get their pool from `xsk_get_pool_from_qid()` when XDP is active and the queue bit is set in `af_xdp_zc_qps`.

The error path unregisters XDP RX queue metadata for main VSIs when context programming or memory model registration fails. A subtle risk is partial configuration: buffer allocation failure is logged but does not fail ring configuration, so later runtime paths must tolerate rings that started with fewer than all buffers populated.

`i40e_vsi_configure()` sequences receive mode/filter scheduling, VLAN restore, DCB ring TC annotations, Tx context programming, and Rx context programming. This is used by open, up, and reinit flows.

## Interrupt and Queue Control Flow

MSI-X queue interrupts are configured in `i40e_vsi_configure_msix()`. The driver writes per-vector RX/TX/SW ITR registers, interrupt rate limits, linked-list heads, and queue interrupt control registers. With XDP enabled, each vector's linked list chains Rx, XDP Tx, and normal Tx queues. Legacy/MSI mode uses `i40e_configure_msi_and_legacy()` for queue zero and non-queue interrupt causes.

`i40e_vsi_request_irq_msix()` requests one IRQ per used q_vector, names it according to Tx/Rx use, registers an affinity-change notifier, and sets CPU affinity hints with `cpumask_local_spread()`. The unwind path removes notifiers, hints, and requested IRQs. `i40e_vsi_free_irq()` tears down the software IRQs and hardware queue linked lists for MSI-X and legacy modes.

`i40e_intr()` handles ICR0 non-queue events and legacy/MSI queue interrupts. It masks AdminQ, MDD, VFLR, reset, PE critical, and unexpected critical causes; schedules NAPI for queue 0 in non-MSI-X mode; schedules PTP work or timestamp handling for timesync; records reset type counters; and schedules the service task before reenabling ICR0 when appropriate.

Queue enable/disable is split into direct register request functions and wait helpers:

- `i40e_control_wait_tx_q()` uses `i40e_pre_tx_queue_cfg()`, writes `QTX_ENA`, and polls `QENA_STAT`.
- `i40e_control_wait_rx_q()` writes `QRX_ENA` and polls `QENA_STAT`.
- `i40e_vsi_start_rings()` enables Rx first, then Tx.
- `i40e_vsi_stop_rings()` disables Rx, waits a fixed Tx gap, then disables Tx and waits for all queues, unless port Tx is suspended and the no-wait path is used.

NAPI is enabled only after rings are started and disabled before rings are cleaned. `i40e_down()` also synchronizes RCU before cleaning XDP Tx rings so in-progress `ndo_xdp_xmit` and XSK wakeups complete.

## DCB, Bandwidth, and mqprio/Channel Behavior

Under `CONFIG_I40E_DCB`, the chunk parses DCBX configuration, determines enabled TCs, configures VEB/VSI bandwidth, suspends/resumes port Tx, and programs DCB hardware directly or through firmware LLDP MIB support. `i40e_hw_dcb_config()` can quiesce all VSIs, suspend port Tx, configure ETS/PFC/Rx packet buffers, notify firmware, reconfigure VEBs/VSIs, wait for queues to disable, and unquiesce VSIs.

`i40e_vsi_config_tc()` is the central TC reconfiguration routine. It programs BW allocation, updates the VSI queue map, optionally reconfigures RSS, sets iWARP queue options, updates VSI params through AdminQ, refreshes local queue map copies, queries BW info, and updates netdev TC mappings. If requested TCs are not valid according to firmware, it retries with the intersection plus TC0.

Hardware mqprio channel mode creates extra VMDq2 channel VSIs for nonzero TCs. `i40e_validate_mqprio_qopt()` requires contiguous queue ranges starting at offset 0, no minimum rates, valid max-rate sum, and enough queues. `i40e_configure_queue_channels()` builds `struct i40e_channel` objects for enabled nonzero TCs, creates channel VSIs, assigns queue ranges, optionally sets BW limits, then triggers a PF reset so Tx queue contexts are rebuilt.

Channel cleanup (`i40e_remove_queue_channels()`) resets ring `ch` pointers, clears per-channel BW limit, deletes associated cloud filters from hardware and the PF list, deletes the channel VSI, frees memory, and resets RSS size bookkeeping. This path is important when mqprio is removed or reconfiguration fails.

## Macvlan L2 Forwarding Offload

The macvlan offload path reserves a subset of queues and creates channel VSIs that serve as subordinate macvlan devices. It is refused when DCB or hardware TC offload is enabled, when vector count is too low, or when the macvlan device is multiqueue.

`i40e_fwd_add()` lazily creates macvlan channels on the first request. It reserves bit 0 for the PF, computes channels and queues per channel from MSI-X vector budget, quiesces the parent VSI, calls `i40e_setup_macvlans()`, unquiesces, allocates an `i40e_fwd_adapter`, binds the subordinate channel to the macvlan netdev, and if the parent is running, calls `i40e_fwd_ring_up()`.

`i40e_fwd_ring_up()` assigns ring `ch` pointers, binds queue ranges to the subordinate netdev, uses a write memory barrier before programming the MAC filter, and adds a perfect MAC filter on the channel VSI. Failure disables macvlan L2 forwarding offload for that vdev and clears affected Rx ring netdev pointers.

`i40e_fwd_del()` and `i40e_del_all_macvlans()` remove channel MAC filters, reset ring channel pointers, clear allocation bits, unbind subordinate channels, and free forwarding adapters. Full channel VSI deletion happens in `i40e_free_macvlan_channels()`.

## TC Flower and Cloud Filters

Cloud filters are the hardware backing for TC flower offload in this chunk. `i40e_parse_cls_flower()` accepts only control, basic, Ethernet addresses, VLAN, IPv4/IPv6 addresses, ports, and encapsulation key ID. It rejects partial masks for MAC/IP/ports/VLAN, IPv6 loopback addresses, tenant ID with IP filters, unsupported transport protocols, and unsupported control flags.

`i40e_set_cld_element()` maps a parsed `i40e_cloud_filter` into AdminQ cloud-filter element data, including MACs, IPv4 or IPv6 destination address, and inner VLAN. Tenant ID is noted as unsupported in the visible code.

Two AdminQ programming variants exist:

- `i40e_add_del_cloud_filter()` uses regular cloud filter commands and a flag table for OMAC/IMAC/VLAN/tenant/IP combinations.
- `i40e_add_del_cloud_filter_big_buf()` supports L4-port-based filters through the big-buffer command path, with restrictions: not both source and destination MAC, nonzero L4 destination port, no UDP big-buffer filters, no source port/source IP matching, and either MAC or destination IP must be valid.

Before adding a big-buffer filter, `i40e_validate_and_set_switch_mode()` ensures the firmware switch mode is cloud-filter mode 2/non-tunneled. `i40e_handle_tclass()` maps TC0 filters to the main VSI SEID and nonzero TC filters to channel VSI SEIDs, requiring a destination port for nondefault TC steering.

`i40e_configure_clsflower()` rejects filters during reset, rejects use when Flow Director sideband filters exist, disables FD sideband if necessary, parses and programs the cloud filter, then records it in `pf->cloud_filter_list` by cookie. Deletes find by cookie, remove from hardware, free the filter, decrement `num_cloud_filters`, and may restore FD sideband state when the cloud-filter list becomes empty.

## Netdev Up/Down/Open/Close Flow

The visible netdev bring-up path is:

1. `i40e_open()` rejects opens during self-test or bad EEPROM state, forces carrier off, forces link up if link-down-on-close/total-port-shutdown policy requires it, calls `i40e_vsi_open()`, and writes global TSO mask registers.
2. `i40e_vsi_open()` allocates Tx and Rx descriptor resources, configures the VSI, requests IRQs for netdev or FDIR VSI, updates real Tx/Rx queue counts for netdev VSIs, and calls `i40e_up_complete()`.
3. `i40e_up_complete()` writes interrupt configuration, starts rings, clears `__I40E_VSI_DOWN`, enables NAPI and IRQs, starts netdev queues/carrier if link is up, replays FDIR sideband filters for the FDIR VSI, and schedules client service.

The down path is the inverse:

- `i40e_down()` disables carrier and Tx queues, masks IRQs, stops rings, optionally forces link down, disables NAPI, and cleans Tx/XDP/Rx rings.
- `i40e_vsi_close()` sets `__I40E_VSI_DOWN`, calls `i40e_down()` if this was the first close, frees IRQs and descriptor resources, clears current netdev flags, and records client service/reset notifications.
- `i40e_close()` is the netdev callback wrapper and does not fail.

`i40e_vsi_open()` performs a PF reset on main-VSI open failure after resource cleanup. That is a notable recovery decision: an open-time setup failure is treated as potentially requiring hardware reinitialization.

## Reset Entry in This Chunk

This chunk ends at the start of `i40e_do_reset()`. The visible portion chooses the largest requested reset. For global reset it writes `I40E_GLGEN_RTRIG` to request a chip-wide reset and relies on the reset-warning interrupt path to shut down and rebuild switch setup. Earlier functions in the chunk set reset request bits in response to Tx timeout, critical interrupts, DCB failures, channel mode changes, and error conditions; later chunks own the full reset/rebuild implementation.

`i40e_tx_timeout()` escalates recovery from PF reset to core reset to global reset and finally marks the device/VSI down if repeated recovery fails. It logs queue hardware state, sets `__I40E_TIMEOUT_RECOVERY_PENDING`, and schedules service work.

## Dependencies and Integration Points

This chunk depends on:

- Linux networking APIs: `net_device_ops`, VLAN callbacks, netdev address sync, NAPI, XDP RX queue metadata, AF_XDP pools, TC mqprio and flower APIs, flow block callbacks, macvlan subordinate channel APIs, rtnl expectations, netpoll, carrier/queue control, XPS, and ethtool EEE access for link messages.
- Kernel platform APIs: PCI/MSI/MSI-X, DMA coherent allocation, RCU, spinlocks, bit operations, hlist/list/hash helpers, workqueues, timers/jiffies, IRQ affinity notifiers, cpumasks, memory barriers, and module metadata.
- i40e shared hardware/AdminQ/HMC layers: `rd32`/`wr32`/`rd64`, `i40e_aq_*` commands, `libie_aq_str()`, HMC queue context helpers, DCB hardware helpers, Flow Director input/filter helpers, PTP helpers, SR-IOV/VF structures, and reset/rebuild helpers defined elsewhere.
- Companion i40e files: descriptor allocation/cleaning, XDP helpers, FDIR programming, RSS register fallback, ethtool feature toggles, probe/remove, service task, VF management, and definitions in `i40e.h`, `i40e_lan_hmc.h`, `i40e_virtchnl_pf.h`, and `i40e_xsk.h`.

The principal integration surfaces are the netdev callbacks, TC offload callbacks, service task bits, AdminQ firmware interface, HMC queue contexts, IRQ/NAPI integration, and reset recovery state machine.

## State and Persistence Behavior

The driver keeps software mirrors for nearly every hardware programming domain:

- MAC/VLAN filters persist in `mac_filter_hash` and are replayed by setting sync-pending bits.
- VLAN memberships persist in `active_vlans`; PVID and VLAN strip mode persist in `vsi->info`.
- RSS user key/LUT pointers override generated defaults and survive reconfiguration.
- TC queue maps, mqprio options, channel lists, and TC-to-SEID maps describe how queue ownership should be rebuilt.
- FDIR filters and cloud filters live in PF hlist state so they can be replayed or deleted during channel/filter teardown.
- Statistics offsets persist until reset/reset-stats so hardware counters can be presented as driver-relative counters.
- PF/VSI state bits serialize down/up/config/reset/filter-sync work and gate service scheduling.

This persistence is essential because resets and close/open cycles do not simply clear all software state. Many operations defer hardware programming to the service task or rebuild path, so correctness depends on state bits and shadow lists accurately describing desired hardware state.

## Risks and Edge Cases

- The filter sync path has multiple partial-failure windows. Allocation failures roll back temp list movement, but AdminQ failures can leave filters marked failed, force overflow promiscuous mode, or require a later service retry.
- `i40e_sync_vsi_filters()` waits with `usleep_range()` while another filter sync is in progress. Long firmware operations can delay callers that need filter convergence.
- Broadcast filters are not regular MAC filters in firmware; they toggle broadcast promiscuous flags. Any future change treating them as normal filters would break current assumptions.
- VF VLAN behavior depends on trust and pruning flags. Untrusted VFs cannot use overflow promiscuous fallback, which is correct for isolation but changes failure behavior relative to PF/main VSI filters.
- Ring configuration can succeed after logging incomplete Rx buffer allocation. Runtime receive paths must handle low-buffer startup conditions.
- XDP/AF_XDP setup mixes queue ID remapping, memory model registration, and pool assignment. Off-by-one errors between normal queues and XDP queues would misprogram pool ownership or interrupt links.
- Interrupt free tears down hardware queue linked lists based on register state. Corrupted or stale next-queue fields could cause incomplete cleanup or incorrect register writes.
- DCB and mqprio reconfiguration quiesce/unquiesce VSIs and may trigger PF reset. Failure paths reset TC config to defaults, but earlier AdminQ side effects may remain until reset/rebuild.
- Channel and macvlan paths repurpose parent VSI queues for child/channel VSIs. Ring `ch` pointer cleanup must remain paired with channel deletion, filter deletion, and subordinate netdev unbinding.
- TC flower cloud filters conflict with Flow Director sideband filters; the code disables FD sideband when adding cloud filters and conditionally restores it only after all cloud filters are gone.
- `i40e_validate_and_set_switch_mode()` may alter firmware switch mode while adding a big-buffer cloud filter. Tests should account for this global PF/device side effect.
- Netdev open failure on the main VSI triggers PF reset. Fault injection around descriptor allocation, VSI configuration, IRQ request, and queue count updates should verify cleanup before reset.
- Link force-up/down reads PHY capabilities twice and may alter advertised PHY type fields. Device/firmware revisions with unusual PHY capability reporting are high-risk.

## Test Signals

Useful validation signals for this chunk include:

- Build/config coverage with `CONFIG_I40E_DCB`, `CONFIG_NET_POLL_CONTROLLER`, XDP, AF_XDP, SR-IOV, PTP, and TC flower enabled and disabled.
- MAC/VLAN tests: set MAC during normal/down/reset states; add/delete unicast/multicast/broadcast filters; VLAN 0 add/delete; PVID add/remove; active VLAN restore after close/open; VF trusted/untrusted VLAN pruning behavior; filter table exhaustion and overflow-promisc enter/exit.
- Stats tests: first-read offset baselining, wraparound for 32-bit and 48-bit counters, QEMU split-counter path, reset-stats behavior, and concurrent stats reads during ring teardown.
- MTU/XDP tests: MTU limits with no XDP, non-fragment XDP, frags-capable XDP, legacy Rx mode, and small-page build_skb mode.
- Ring tests: Tx/Rx HMC context programming failure injection, AF_XDP pool present/absent, XDP RXQ registration failure, low Rx buffer allocation, XPS initialization once per ring.
- Interrupt tests: MSI-X request/unwind, IRQ affinity notifier cleanup, legacy shared IRQ with no pending interrupt, AdminQ/MDD/VFLR/reset/PTP interrupt bits, critical-error reset scheduling, netpoll execution.
- Queue tests: enable/disable timeout paths, XDP Tx queue offset waits, stop-rings with and without port-suspended state, no-wait stop followed by aggregate wait.
- DCB/mqprio tests: noncontiguous TC detection, firmware valid-TC fallback, PFC/ETS reconfiguration, port Tx suspend/resume failure, mqprio contiguous queue validation, max-rate bounds, channel creation failure cleanup, PF reset after channel setup.
- Macvlan tests: unsupported with DCB or TC offload, vector-budget queue partitioning, L2 forwarding filter add failure, subordinate channel bind/unbind, deleting all macvlans before channel free.
- TC flower tests: unsupported dissector keys, partial masks, IPv4/IPv6 address handling, L4 protocol restrictions, tenant ID rejection with IP filters, nonzero TC requiring destination port, Flow Director conflict handling, cloud-filter delete by cookie.
- Lifecycle tests: `i40e_open()` rejection during testing/bad EEPROM, `i40e_vsi_open()` fault injection at Tx setup/Rx setup/configure/IRQ/queue count/up-complete, close idempotence, and Tx-timeout reset escalation.

## Cross-Chunk References

The following required behavior is called from this chunk but implemented later or in companion files:

- Full reset and rebuild: `i40e_prep_for_reset()`, `i40e_reset()`, `i40e_rebuild()`, `i40e_reset_and_rebuild()`, `i40e_handle_reset_warning()`, and service subtasks continue after this chunk.
- Probe/remove/module registration and interrupt-scheme allocation are later in the same file.
- Descriptor allocation, packet clean paths, XDP transmit/wakeup helpers, Flow Director add/delete helpers, PTP work, VF management, ethtool RSS register fallback, and many AdminQ wrappers live in other i40e/libie sources.
- `struct net_device_ops` and ethtool operation tables that point to these callbacks are outside this line range.

### subset-b-004459: lines 9300-16679

# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_main.c lines 9300-16679

## Chunk Scope

This chunk covers the high-level PF lifecycle for the Intel i40e Ethernet driver: reset recovery, AdminQ event handling, Flow Director recovery, link/DCB updates, VSI/VEB allocation and rebuild, RSS/XDP/netdev operations, PCI probe/remove, suspend/resume, PCI error recovery, shutdown, and module registration. It sits after the lower-level queue, interrupt, filter, DCB, channel, and open/close helpers from earlier in the file and wires those helpers into the device lifetime and Linux networking callbacks.

## Purpose and Responsibilities

- Dispatch pending reset requests from `pf->state`, perform PF/core/global resets, and rebuild firmware-visible switch state while preserving software state such as filters, channels, bandwidth limits, promiscuity, PTP time, and VF resources.
- Run the periodic service task that coordinates filter sync, reset recovery, MDD/VFLR handling, watchdog/statistics updates, FDir maintenance, client notifications, and AdminQ event draining.
- Manage firmware switch elements: the main PF VSI, FDir VSI, SR-IOV/VMDq/channel VSIs, and VEB bridge elements, including reconstruction after reset and deletion during remove.
- Initialize the PF during PCI probe: PCI resources, MMIO mapping, AdminQ, NVM/firmware capability discovery, software feature flags, queue/vector budgets, LAN HMC, switch setup, PTP, DCB, SR-IOV, UDP tunnel offload, iWARP client integration, and devlink registration.
- Expose netdev callbacks for feature toggles, FDB/bridge operations, XDP/AF_XDP setup, UDP tunnel ports, physical port IDs, hwtstamp, and VF controls.
- Provide PM and PCI error paths that quiesce IO, preserve wake settings, tear down/restores interrupts, and rebuild the device.

## Important APIs, Types, and Entry Points

- `struct i40e_pf`: central PF state holder. This chunk heavily mutates `pf->state`, `pf->flags`, `pf->hw`, `pf->vsi[]`, `pf->veb[]`, queue/vector lump trackers, FDir counters, cloud filter lists, DCB state, WoL state, timers, work item, and PCI/devlink/client bookkeeping.
- `struct i40e_vsi`: software representation of PF, FDir, SR-IOV, VMDq/channel, or iWARP VSIs. Allocation paths set queue counts, ring arrays, q_vectors, netdevs, MAC filters, RSS settings, XDP pointers, uplinks, and hardware SEIDs.
- `struct i40e_veb`: software representation of hardware VEB bridge elements. This chunk allocates, adds, configures VEPA/VEB mode, queries bandwidth, reconstructs, releases, and recursively deletes VEB branches.
- Reset/rebuild functions: `i40e_do_reset_safe()`, `i40e_prep_for_reset()`, `i40e_reset()`, `i40e_rebuild()`, `i40e_reset_and_rebuild()`, and `i40e_handle_reset_warning()`.
- Service/event functions: `i40e_service_task()`, `i40e_service_timer()`, `i40e_reset_subtask()`, `i40e_watchdog_subtask()`, `i40e_clean_adminq_subtask()`, `i40e_handle_link_event()`, `i40e_handle_lan_overflow_event()`, and, with DCB, `i40e_handle_lldp_event()`.
- FDir helpers: `i40e_get_current_fd_count()`, `i40e_get_global_fd_count()`, `i40e_fdir_check_and_reenable()`, `i40e_fdir_flush_and_replay()`, `i40e_fdir_sb_setup()`, and `i40e_fdir_teardown()`.
- VSI/VEB lifecycle: `i40e_vsi_mem_alloc()`, `i40e_vsi_setup()`, `i40e_vsi_reinit_setup()`, `i40e_add_vsi()`, `i40e_vsi_release()`, `i40e_vsi_clear()`, `i40e_veb_setup()`, `i40e_add_veb()`, `i40e_veb_release()`, `i40e_switch_branch_release()`, and `i40e_setup_pf_switch()`.
- Interrupt/RSS/resource setup: `i40e_init_msix()`, `i40e_init_interrupt_scheme()`, `i40e_restore_interrupt_scheme()`, `i40e_setup_misc_vector()`, `i40e_vsi_alloc_q_vectors()`, `i40e_pf_config_rss()`, `i40e_config_rss()`, `i40e_get_rss()`, and `i40e_reconfig_rss_queues()`.
- Netdev and XDP integration: `i40e_netdev_ops`, `i40e_config_netdev()`, `i40e_set_features()`, `i40e_xdp_setup()`, `i40e_xdp()`, `i40e_queue_pair_disable()`, and `i40e_queue_pair_enable()`.
- PCI/module entry points: `i40e_probe()`, `i40e_remove()`, `i40e_shutdown()`, `i40e_suspend()`, `i40e_resume()`, `i40e_err_handler`, `i40e_driver`, `i40e_init_module()`, and `i40e_exit_module()`.

## Control Flow and State Machines

### Reset and Rebuild

Reset requests are accumulated as bits in `pf->state` and consumed by `i40e_reset_subtask()`. The subtask clears request bits, gives priority to `__I40E_RESET_INTR_RECEIVED` recovery, and avoids reset work while the PF is down or configuration is busy. `i40e_do_reset()` chooses between global, core, PF reset, PF reset plus main VSI reinit, VSI reinit, and VSI down requests. User-facing calls can use `i40e_do_reset_safe()`, which serializes with `rtnl_lock()`.

`i40e_prep_for_reset()` is the reset prologue. It guards with `__I40E_RESET_RECOVERY_PENDING`, notifies VFs if the Admin Send Queue is alive, quiesces all active VSIs, clears XPS state, invalidates VSI SEIDs, shuts down AdminQ and HMC, and saves PTP hardware time. `i40e_reset()` performs the PF reset and records `pfr_count` or `__I40E_RESET_FAILED`. `i40e_rebuild()` then rebuilds AdminQ, capabilities, LAN HMC, DCB state, PF switch, VEBs, VSIs, cloud filters, channels, MSS workaround, autoneg restart, misc IRQ, flow-control drop filter, queues, promiscuous mode, VFs, and driver version reporting. It also has a recovery-mode branch that only restores minimal resources and ethtool operations as needed.

The rebuild path depends on local switch arrays retaining intent while firmware state disappears across reset. If VEB reconstruction fails for the main VEB, it falls back to a simple PF VSI connection to the MAC SEID. Channel VSIs and cloud filters are replayed after the main VSI exists again.

### Service Task

`i40e_service_timer()` periodically reschedules `service_task` via the driver's workqueue. `i40e_service_task()` exits early if reset recovery or suspend is active, serializes with `__I40E_SERVICE_SCHED`, then runs a fixed sequence outside recovery mode: hung recovery detection, filter sync, reset handling, malicious driver detection, VFLR processing, watchdog updates, FDir maintenance, client reset/L2 notifications, and a second filter sync. In recovery mode it only runs reset handling before cleaning AdminQ. After AdminQ drain it clears the schedule bit with a memory barrier and immediately reschedules if work exceeded one timer period or event bits remain.

`i40e_clean_adminq_subtask()` clears AdminQ error bits in ARQ/ASQ length registers, allocates an AQ event buffer, drains up to `I40E_AQ_WORK_LIMIT` events, dispatches link, VF mailbox, LLDP MIB, LAN overflow, peer, and NVM completion opcodes, then re-enables AdminQ interrupt cause. Link and LLDP handlers take RTNL because they update netdev and DCB/VSI state.

### Link, DCB, and Notifier Behavior

`i40e_link_event()` forces a fresh firmware link query, manages temporary link polling on query errors, compares old/new link and speed, updates carrier and TX queues for the main VSI or VEB-connected VSIs, notifies VFs, updates PTP clock increments, and for software DCB falls back to single-TC defaults on link down. `i40e_handle_link_event()` ignores ARQ link payload for state refresh but uses it to report high-temperature or unsupported-module conditions.

Under `CONFIG_I40E_DCB`, `i40e_handle_lldp_event()` handles nearest-bridge local/remote MIB changes. Remote updates refresh `hw->remote_dcbx_config`; local updates fetch the new DCBX config, compare ETS/PFC/app tables with `i40e_dcb_need_reconfig()`, flush DCBNL apps, quiesce VSIs, reconfigure DCB, resume port TX, wait for queues to disable, then unquiesce and notify clients of L2 changes.

### VSI, VEB, Queue, and Interrupt Lifecycles

`i40e_vsi_setup()` is the main VSI constructor. It validates or creates the uplink VEB, allocates the software VSI slot, reserves queue lumps, adds or retrieves the hardware VSI, configures netdev/devlink for main/VMDq VSIs, registers the netdev, sets DCBNL for the main netdev when enabled, allocates vectors, allocates rings, maps rings to q_vectors, resets stats, and configures RSS for VMDq when supported. Error unwinds delete hardware elements, destroy devlink ports, unregister/free netdevs, free vectors/rings, and clear the VSI slot.

`i40e_add_vsi()` builds `struct i40e_vsi_context` differently by type. The main PF VSI is retrieved from firmware rather than added; FDir, VMDq, and SR-IOV VSIs are created through AQ. It applies source pruning changes, MFP queue map updates, TC config, VEB loopback flags, iWARP queue options, SR-IOV VLAN/security settings, and marks existing MAC filters as `I40E_FILTER_NEW` so the filter sync subtask reloads them after resets.

`i40e_vsi_release()` refuses VEB owners and a running PF main VSI, unregisters or closes netdev-backed VSIs, disables IRQs, destroys devlink for the main VSI, marks filters for deletion, syncs filters, deletes the hardware element, frees q_vectors/netdev/rings/software arrays, and may release the uplink VEB if no non-owner VSIs remain. VEB deletion uses `i40e_switch_branch_release()` for recursive branch cleanup.

`i40e_init_msix()` budgets MSI-X vectors among misc, LAN/RSS, FDir sideband, iWARP, and VMDq. It degrades feature counts if the platform grants fewer vectors, disabling FDir, VMDq, or iWARP when none remain. `i40e_init_interrupt_scheme()` falls back from MSI-X to MSI to legacy IRQ and creates an IRQ lump tracker with vector 0 reserved for misc. `i40e_restore_interrupt_scheme()` reacquires vectors after suspend, allocates q_vectors for all VSIs, remaps rings, and reinitializes the misc vector.

Queue-pair hot toggles (`i40e_queue_pair_disable()` and `i40e_queue_pair_enable()`) are protected by `__I40E_CONFIG_BUSY`, disable or enable IRQ/NAPI/rings, clean rings and stats on disable, configure Tx/XDP/Rx rings on enable, and use `i40e_control_wait_tx_q()`, `i40e_control_rx_q()`, and `i40e_pf_rxq_wait()` for hardware synchronization. One risk is that `i40e_queue_pair_disable()` does not call `i40e_exit_busy_conf()` on its path in this chunk; callers must ensure the busy bit is cleared elsewhere or this is a latent lockout bug.

### Probe, Remove, PM, and Error Recovery

`i40e_probe()` performs the full PCI bring-up: enable memory BARs, set DMA mask, request regions, allocate PF, map registers after BAR-size validation, initialize IDs and AQ locks, clear PXE mode on old revisions, clear hardware, determine MAC type, handle repeated resets/recovery, initialize shared code and AdminQ, report firmware/NVM versions, verify EEPROM, discover capabilities, initialize software flags/resource trackers, optionally enter minimal recovery mode, initialize/configure LAN HMC, stop firmware LLDP where supported, resolve MAC address, set PTP pins, initialize DCB, configure service timer/work, read WoL setting, determine queue use, initialize interrupts, configure UDP tunnel offload table, allocate VSI table, set up PF switch, open FDir VSI if present, configure PHY interrupt masks, initialize MDD rate limiting, apply MSS/autoneg workarounds, clear `__I40E_DOWN`, set misc vector, allocate existing VFs, reserve iWARP vectors, initialize debug/client service, start timer, log PCI link capabilities, fetch PHY/FEC capabilities, set MAC frame size, add flow-control drop filter, mark LED/retimer capabilities, print features, and register devlink.

Probe has many labeled unwind paths. The major cleanup sequence tears down VSIs, PTP pins, interrupt capability, timer, LAN HMC, queue pile, AdminQ/MMIO/PF memory, PCI regions, and device enablement. Some labels intentionally share cleanup for multiple failure points.

`i40e_remove()` unregisters devlink/debug/PTP, disables RSS, blocks rebuild by taking `__I40E_RESET_RECOVERY_PENDING` and setting `__I40E_IN_REMOVE`, frees VFs, suspends timers/work, closes clients, tears down FDir/cloud filters, removes VEB branches and VSIs, deletes iWARP client devices, shuts down HMC/AdminQ, destroys AQ locks, clears interrupt scheme and remaining rings/VSIs/VEBs, frees trackers, unmaps MMIO, frees PF, releases PCI regions, and disables the device. Recovery-mode removal has a shorter netdev-only path before common unmap/AdminQ cleanup.

`i40e_io_suspend()` and `i40e_io_resume()` are shared by PM and error handling. Suspend marks down, stops timer/work, closes clients, enables multicast magic WoL if supported, takes RTNL, preps for reset, programs wake registers, and clears interrupts. Resume takes RTNL, restores interrupts, clears down, reset/rebuilds, clears suspended, and restarts the timer. PCI error handlers call these or the reset prologue/rebuild around slot resets and SR-IOV MSI restoration.

## State and Persistence Behavior

- Persistent software intent is held in `pf->flags`, `pf->state`, `pf->vsi[]`, `pf->veb[]`, filter lists, channel lists, bandwidth settings, RSS user key/LUT buffers, XDP program pointers, and VF structures. Reset rebuild relies on these structures remaining valid while hardware/AdminQ/HMC state is destroyed and recreated.
- Hardware state is programmed through AQ commands and MMIO registers. It includes switch element SEIDs, VSI contexts, VEB bandwidth/stats, RSS keys/LUT/HENA, PF/VF MDD registers, interrupt cause registers, queue control registers, NVM-derived OEM/WoL/total-port-shutdown values, FEC flags, wake registers, and flow-control drop filters.
- `pf->state` bits serialize or gate asynchronous paths: down, suspended, reset recovery pending, reset failed, AdminQ pending, service scheduled, config busy, recovery mode, remove-in-progress, FDir auto-disabled/flush requested, MDD print/event pending, temporary link polling, and client notifications.
- `pf->flags` advertise capability/configuration state: MSI/MSI-X, RSS, DCB, SR-IOV, FDir ATR/SB, VMDq, iWARP, MFP, VEB mode, PTP, total-port-shutdown, WoL-related behavior, MDD auto-reset, and feature-specific inactive states.
- Timers/work persist the service loop until suspend/remove/shutdown. Probe and resume arm the timer; remove/shutdown/suspend delete or shutdown it and cancel work.
- User-configured RSS key/LUT buffers persist across most reconfigurations but are discarded when RSS queue count shrinks below the previous VSI RSS size.

## Dependencies and Integration Points

- Linux PCI and PM: `struct pci_driver`, `pci_error_handlers`, BAR mapping, DMA mask setup, MSI/MSI-X APIs, PCI state save/restore, power-state and wake APIs.
- Linux netdev stack: `net_device_ops`, feature negotiation, carrier state, queue start/stop, FDB and bridge netlink operations, UDP tunnel NIC offload, XDP/AF_XDP, NAPI, ethtool setup, hwtstamp hooks, VLAN/macvlan handling, and RTNL locking.
- Intel AdminQ/shared-code APIs: capabilities discovery, switch config queries, VSI/VEB add/delete/update, PHY/link/FEC, LLDP/DCB, RSS key/LUT, UDP tunnel ports, partition bandwidth, NVM reads, MAC writes, and filter control.
- SR-IOV/VF control: VF reset notification, VF mailbox processing, VF MDD detection/reset, VFLR processing, VF allocation/free, VF link notifications, and SR-IOV netdev callbacks.
- DCB and PTP modules: DCBX config comparison/reconfigure, DCBNL app flushing/setup, PTP pin allocation, PTP init/stop, PTP time save, increment update, and TX/RX hang detection.
- Client/iWARP integration: client device add/delete, MSI-X info updates, client close/reset/L2-change notifications, and a neighbor private length requirement for `i40iw_net_event()`.
- Devlink/debugfs: main VSI devlink port creation/destruction and PF debug init/exit.

## Risks and Edge Cases

- Reset/rebuild ordering is fragile: AdminQ, HMC, switch, interrupts, VSIs, VEBs, filters, channels, clients, VFs, and PTP each have dependencies. Missing one replay step can leave software state apparently valid but firmware state absent.
- Locking context matters. Several paths explicitly require RTNL (`i40e_do_reset_safe()`, feature changes, bridge setlink, RSS reconfig, suspend/resume rebuild sections), while service work uses state bits and may schedule itself immediately. Mixing direct reset calls without the expected lock can race netdev registration or queue changes.
- Recovery mode intentionally limits functionality and has separate interrupt/netdev setup. Paths must respect `__I40E_RECOVERY_MODE` and `__I40E_IN_REMOVE` to avoid normal rebuild or queue work against a minimally initialized PF.
- MSI-X vector budgeting dynamically disables features. Test coverage should include partial vector grants, MSI fallback, and legacy IRQ mode because FDir, iWARP, VMDq, SR-IOV, RSS, and DCB assumptions change.
- `i40e_handle_lan_overflow_event()` derives a VF index from hardware fields and indexes `pf->vf[vf_id]`; correctness depends on firmware-provided PF/VF queue metadata being valid for allocated VFs.
- FDir counter maintenance has type-specific decrements. The `SCTP_V6_FLOW` case decrements `fd_udp6_filter_cnt` in this chunk, which looks suspicious because the IPv6 user SCTP path decrements `fd_sctp6_filter_cnt`.
- `i40e_queue_pair_disable()` enters `__I40E_CONFIG_BUSY` but this chunk does not clear it before return, unlike `i40e_queue_pair_enable()`. If no external caller clears it, queue-pair disable can leave future configuration blocked.
- Probe unwind and remove touch many shared resources. Double-free risk is mitigated by flags/nulling, but paths involving recovery mode, failed netdev registration, or partially allocated `pf->vsi` require careful review.
- XDP setup resets rings when XDP state changes and swaps `vsi->xdp_prog` before rebuild. Error paths after `xchg()` can leave program ownership or ring buffer allocation expectations subtle, especially with AF_XDP zero-copy pools.
- DCB handling for X710-T*L 2.5G/5G link speeds changes `I40E_FLAG_DCB_CAPABLE` based on link speed and firmware responses; tests must cover link-speed transitions as well as LLDP local and remote MIB events.

## Test Signals and Validation Ideas

- Probe/remove: successful module load/unload, `i40e_probe()` logs firmware/NVM/MAC/features, devlink registration, no leaks or warnings on repeated bind/unbind, and correct recovery-mode minimal netdev behavior when firmware reports recovery.
- Reset/rebuild: trigger PF reset, core/global reset, EMP reset, TX timeout recovery, RSS queue reconfig, XDP attach/detach, and bridge-mode changes; verify netdev carrier, queues, filters, channels, VFs, PTP, promiscuity, and UDP tunnel ports are restored.
- AdminQ events: inject or exercise link changes, unsupported/high-temperature module reports, VF mailbox messages, LLDP MIB updates, LAN overflow, NVM completion, and unknown opcodes; verify event bits clear and interrupts are re-enabled.
- FDir: fill/flush/replay filter table, check SB/ATR auto-disable and re-enable thresholds, validate invalid filter deletion counters, and specifically test SCTP IPv6 counter accounting.
- Interrupt modes: boot or fault-inject with full MSI-X, limited MSI-X, MSI-only, and legacy IRQ; verify vector distribution logs, feature disabling, q_vector mapping, misc interrupt setup, and suspend/resume restoration.
- VSI/VEB: create/release VMDq/channel/SR-IOV VSIs, bridge VEPA/VEB transitions, floating VEB deletion, recursive branch removal, and reset-time VEB reconstitution with cloud filters and bandwidth limits.
- Netdev features: toggle RXHASH, ntuple, VLAN stripping, HW TC with active cloud filters, loopback, L2 forwarding offload with macvlans, FDB add, bridge get/setlink, UDP tunnel port add/delete, and features_check for encapsulated header limit violations.
- XDP/AF_XDP: attach/detach programs across MTU limits, attach with frags support, zero-copy pool setup, redirect feature toggling, and queue wakeups after reset.
- PM/PCI error: suspend/resume, hibernate-like vector teardown/restore, shutdown with WoL enabled/disabled, PCI AER detected/slot_reset/reset_prepare/reset_done/resume, and SR-IOV VF MSI restoration after PCI reset.
