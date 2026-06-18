# subset-b-004849

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/wmm.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/wmm.c

Purpose: implements the mwifiex WMM transmit scheduler and QoS state machine. It maps IP/802.11 priorities to WMM access categories and TIDs, tracks per-TID/per-receiver-address queues, parses firmware WMM status responses, builds association WMM IEs, and integrates WMM queueing with 11n AMPDU/AMSDU aggregation and TDLS.

Important APIs/functions: exports `mwifiex_wmm_init`, `mwifiex_wmm_setup_queue_priorities`, `mwifiex_wmm_setup_ac_downgrade`, `mwifiex_wmm_add_buf_txqueue`, `mwifiex_wmm_add_buf_bypass_txqueue`, `mwifiex_wmm_process_tx`, `mwifiex_process_bypass_tx`, `mwifiex_ret_wmm_get_status`, `mwifiex_wmm_process_association_req`, `mwifiex_wmm_compute_drv_pkt_delay`, `mwifiex_wmm_get_queue_raptr`, `mwifiex_wmm_get_ralist_node`, `mwifiex_rotate_priolists`, `mwifiex_update_ralist_tx_pause`, `mwifiex_update_ralist_tx_pause_in_tdls_cs`, `mwifiex_wmm_del_peer_ra_list`, and `mwifiex_clean_txrx`. Internal helpers allocate RA-list nodes, derive queue priorities from WMM parameter IEs, downgrade AC/TID when admission control disables an AC, pick the highest priority non-paused RA list, and send or requeue packets.

Control flow: initialization seeds aggregation priorities, disables AMSDU for TIDs 6/7 and optionally via the `disable_tx_amsdu` module parameter, resets BA parameters and RX sequence state, and initializes queue counters. Association builds a WMM information TLV when the BSS requires WMM or HT operation needs it. Firmware WMM status responses are parsed as TLVs; queue-status TLVs update `priv->wmm.ac_status`, a vendor-specific WMM parameter IE refreshes `curr_bss_params`, then queue priorities and downgrade mappings are recomputed. TX enqueue derives the receiver address, handles TDLS setup/in-progress states, drops disconnected data, downgrades the TID if needed, selects or creates a RA list, appends the skb, updates BA and total packet counters, and increments either the active queued count or paused count. TX processing repeatedly selects the highest-priority non-paused RA list across BSS priorities, starts BA setup when traffic crosses a randomized threshold, chooses AMSDU aggregation when possible, and sends either an aggregate or a single packet. Bus backpressure marks packets as requeued; later `mwifiex_send_processed_packet` bypasses normal TX processing and calls `host_to_card` directly.

State and persistence: queue state lives in `priv->wmm`, `tid_tbl_ptr[]`, per-RA `mwifiex_ra_list_tbl` nodes, `bypass_txq`, `tdls_txq`, and `ack_status_frames`. Counters are split between active queued packets (`tx_pkts_queued`), paused packets (`pkts_paused[]`), per-TID packets out, per-RA `total_pkt_count`, and BA trigger counts. `highest_queued_prio` is an atomic cursor used as a priority scan hint and is reset whenever pause state changes. WMM IE information persists in current BSS parameters, while aggregation policy persists in `aggr_prio_tbl`. No on-disk persistence exists; state is runtime driver/firmware coordination.

Dependencies and integration: depends on mwifiex core structures from `decl.h`, `main.h`, firmware TLV definitions from `fw.h`, 11n helpers from `11n.h`, Linux skb queues, atomics, spinlocks, TDLS helpers, adapter bus `if_ops`, and cfg80211/mac80211 concepts such as BSS modes and WMM/HT capabilities. It feeds `mwifiex_process_tx`, `mwifiex_11n_aggregate_pkt`, BA add/delete commands, firmware WMM commands, and completion callbacks.

Risks: RA-list and packet counters must stay balanced across enqueue, pause/unpause, delete, successful TX, and EBUSY requeue paths; a mismatch can wedge queues or underflow paused counts. `mwifiex_wmm_get_highest_priolist_ptr` returns a RA pointer after dropping the spinlock, so later users must revalidate with `mwifiex_is_ralist_valid`, which this file does in send paths. WMM TLV parsing bounds-checks TLV length but silently stops on malformed/default TLVs, so firmware format changes can leave stale AC state. TDLS setup queues can grow until cleaned or flushed. BA threshold randomization is time-derived rather than cryptographic, which is acceptable for scheduling but not a security boundary. Cleanup must run with RX/TX quiesced enough to avoid freeing active RA nodes.

Test signals: exercise association with and without WMM/HT, firmware `WMM_GET_STATUS` responses including disabled ACM ACs, TDLS setup/in-progress/complete transitions, STA/AP/uAP RA-based queueing, paused station queues, AMSDU/AMPDU enable/disable, EBUSY requeue from SDIO/USB/PCIe bus ops, disconnect cleanup, and delayed packet computation under long queueing. Useful runtime signals are queue counters returning to zero, no stuck `highest_queued_prio`, successful BA setup/teardown, and absence of skb completion leaks on cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/wmm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/wmm.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/wmm.h

Purpose: declares the mwifiex WMM API surface and small inline helpers used by the mwifiex data path. It defines bit masks for WMM AC/AIFSN and ECW fields, exposes priority-conversion tables, and makes queue management functions available to association, command, 11n, TDLS, and bus-specific code.

Important APIs/types/functions: defines `enum ieee_types_wmm_aciaifsn_bitmasks` with `MWIFIEX_AIFSN`, `MWIFIEX_ACM`, and `MWIFIEX_ACI`; defines `enum ieee_types_wmm_ecw_bitmasks` with `MWIFIEX_ECW_MIN` and `MWIFIEX_ECW_MAX`; declares external `mwifiex_1d_to_wmm_queue[]` and `tos_to_tid_inv[]`; provides inline `mwifiex_get_tid` and `mwifiex_wmm_is_ra_list_empty`; declares enqueue, bypass, RA-list, TX processing, delay, association, status, downgrade, pause, and init functions implemented mainly in `wmm.c`.

Control flow: callers include this header to retrieve the TID at the head of a RA-list queue, test whether a TID RA-list is empty, enqueue frames into normal or bypass queues, process queued frames, update queue state from firmware or association IEs, and clean up per-peer RA-list state. The inline helpers are deliberately simple and require the caller to use the same locking discipline as the owning WMM code.

State and persistence: this header owns no storage except declarations for shared constant mapping arrays. The helpers read `struct mwifiex_ra_list_tbl` skb queues and return transient queue state. Persistent runtime state remains in `struct mwifiex_private` and `struct mwifiex_wmm_desc`.

Dependencies and integration: depends on mwifiex private structs declared elsewhere, Linux `list_head` and `sk_buff_head`, and WMM bit layout defined by 802.11/WMM firmware contracts. It is the interface between `wmm.c` and other mwifiex modules that need TX scheduling or RA-list visibility.

Risks: inline helpers do not acquire locks; using them without holding `ra_list_spinlock` or an otherwise stable queue context can race with enqueue/dequeue/delete. `mwifiex_get_tid` returns 0 for an empty RA list, so callers must not treat that as an actual queued TID unless they already know a frame exists. Extern table declarations require exactly one definition with matching semantics.

Test signals: compile coverage should catch signature drift between the header and implementation. Runtime coverage should include callers using `mwifiex_get_tid` only after non-empty checks and RA-list emptiness tests under concurrent queue update scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/wmm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwl8k.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwl8k.c

Purpose: implements the Marvell TOPDOG `mwl8k` PCI mac80211 driver for 88w8363/88w8687/88w8366/88w8764 devices. It covers PCI probe/remove, asynchronous firmware loading and fallback, hardware reset, DMA RX/TX rings, firmware command submission, STA/AP firmware differences, mac80211 callbacks, crypto/key commands, WMM/EDCA, BA/AMPDU streams, scan/survey behavior, and firmware restart.

Important APIs/types/functions: central types are `struct mwl8k_priv`, `struct mwl8k_vif`, `struct mwl8k_sta`, `struct mwl8k_rx_queue`, `struct mwl8k_tx_queue`, `struct mwl8k_ampdu_stream`, `struct rxd_ops`, and many packed firmware command/descriptor structs. Major entry points are `mwl8k_probe`, `mwl8k_remove`, `mwl8k_start`, `mwl8k_stop`, `mwl8k_tx`, `mwl8k_add_interface`, `mwl8k_remove_interface`, `mwl8k_config`, `mwl8k_bss_info_changed`, `mwl8k_configure_filter`, `mwl8k_set_key`, `mwl8k_sta_add`, `mwl8k_sta_remove`, `mwl8k_conf_tx`, `mwl8k_get_stats`, `mwl8k_get_survey`, `mwl8k_ampdu_action`, and scan callbacks. Firmware helpers include `mwl8k_request_firmware`, `mwl8k_fw_state_machine`, `mwl8k_load_firmware`, `mwl8k_probe_hw`, `mwl8k_reload_firmware`, `mwl8k_post_cmd`, and many `mwl8k_cmd_*` builders.

Control flow: PCI probe maps SRAM/register BARs, chooses preferred and alternate firmware based on hardware and `ap_mode_default`, and starts asynchronous firmware loading. The firmware callback loads helper and preferred/alternate images, initializes mac80211 capabilities, allocates DMA cookie and rings, probes firmware hardware spec, configures defaults, and registers the hw. Start installs IRQs, enables tasklets/interrupt masks, turns radio on, and initializes sniffer/pre/post-scan/rate/WMM state. TX adds a firmware DMA header, chooses WMM or AMPDU queue, maps TXWI/data, fills descriptors, kicks firmware, and later reclaims descriptors from a TX tasklet. RX tasklet processes descriptors via STA or AP `rxd_ops`, handles beacon capture for finalize-join, applies hardware crypto status flags, removes the DMA header, and submits frames to mac80211. Firmware commands are serialized by a recursive firmware mutex; command posting stops queues, waits for TX rings to drain, optionally stops AP BSSes for disruptive commands, DMA-posts the command, waits for an interrupt completion, then restores BSS/queue state. BA streams are started opportunistically after traffic thresholds, checked against hardware queues, created on mac80211 `TX_OPERATIONAL`, and destroyed on stop/watchdog/station removal. Firmware restart stops queues, completes any pending command, reloads the current firmware image, reprobes hardware, and asks mac80211 to reconfigure.

State and persistence: runtime state is entirely in kernel memory and device firmware. `mwl8k_priv` holds firmware images, DMA rings, per-queue offsets, interrupt/tasklet/work structures, command wait completions, a recursive firmware lock owner/depth, pending TX count, radio/sniffer/WMM flags, BA stream table, survey samples, interface list, running BSS bitmap, MAC ID bitmaps, beacon capture state, and restart state. `mwl8k_vif` stores firmware MAC ID, local sequence number, WEP key copies used to replay keys to new stations, BSSID, and hardware crypto state. TX and RX descriptors persist in coherent DMA memory until deinit. Firmware command structures are transient and packed to the device ABI.

Dependencies and integration: integrates with Linux PCI, firmware loader, DMA API, interrupt/tasklet/workqueue infrastructure, mac80211/cfg80211, netdevice multicast lists, debug/wiphy logging, and Marvell firmware ABI/register layout. AP firmware uses AP-specific RX descriptors and queue SRAM offsets; STA firmware uses STA descriptors and peer-id based TX. It relies on mac80211 for interface lifecycle, BA session callbacks, TX status, RX delivery, scan callbacks, and hw restart.

Risks: command serialization is complex because it waits for TX drain while interrupts/tasklets and firmware restart can also manipulate completions; missed completions or stale `hostcmd_wait` can wedge commands. TX ring accounting (`pending_tx_pkts`, queue `len/head/tail`, descriptor ownership) must stay synchronized across normal reclaim, forced reclaim, ring drain timeout, and firmware reset. AP/STA firmware switching tears down and recreates rings/interfaces, so stale MAC IDs, WEP key replay, or BA streams can leak if restart paths diverge. Packed firmware structs and register constants are ABI-sensitive. RX beacon capture stores a copied skb globally for finalize-join and must be cancelled/freed on stop. Hardware crypto status handling assumes firmware-stripped headers and MMIC error formats. Several paths call command helpers and ignore return values for setup best-effort operations, which can hide partial configuration failures.

Test signals: useful coverage includes module probe/remove for all PCI IDs, firmware helper/preferred/alternate fallback, STA/AP firmware switching via interface creation, start/stop cycles, IRQ TX/RX processing, TX ring saturation and forced reclaim, command timeout and firmware restart, AP beacon DS Params injection, multicast/promisc/sniffer filter changes, WEP/TKIP/CCMP key install/remove, station add/remove with BA active, AMPDU start/stop/watchdog events, software scan survey updates, and mac80211 restart reconfiguration. Runtime signals include no stuck TX rings, no command timeouts under normal operation, correct hw registration bands/caps, and balanced DMA maps/unmaps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwl8k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/Kconfig

Purpose: provides the top-level Kconfig vendor gate for MediaTek wireless drivers. `WLAN_VENDOR_MEDIATEK` controls whether MediaTek-specific driver prompts are visible and sources the `mt7601u` and `mt76` driver families.

Important APIs/types/functions: defines `config WLAN_VENDOR_MEDIATEK` as a bool defaulting to `y`; within the vendor conditional it sources `drivers/net/wireless/mediatek/mt7601u/Kconfig` and `drivers/net/wireless/mediatek/mt76/Kconfig`.

Control flow: during kernel configuration, selecting or defaulting this vendor option to yes exposes MediaTek subdriver configuration. Selecting no hides those prompts without directly changing built objects except through the absence of selected child configs.

State and persistence: persists only in the generated kernel `.config` as `CONFIG_WLAN_VENDOR_MEDIATEK`. No runtime state exists.

Dependencies and integration: integrates with the kernel wireless Kconfig hierarchy under `drivers/net/wireless`. Child Kconfig files define actual tristate modules and dependencies.

Risks: if the vendor option is disabled, all MediaTek subdrivers become unreachable even if a user expects a specific device driver. Adding new MediaTek families requires adding a `source` line here or they will not appear in menuconfig.

Test signals: Kconfig/menuconfig coverage should verify the vendor menu appears by default, disappears when disabled, and exposes `mt7601u` and `mt76` options when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/Makefile

Purpose: wires top-level MediaTek wireless Kconfig symbols to subdirectory builds.

Important APIs/types/functions: adds `mt7601u/` when `CONFIG_MT7601U` is enabled and `mt76/` when `CONFIG_MT76_CORE` is enabled.

Control flow: kbuild descends into selected subdirectories based on the final kernel configuration. This file does not build objects directly; it delegates to each family Makefile.

State and persistence: no runtime state. Build state is represented by kbuild object lists and generated modules.

Dependencies and integration: depends on child directories providing their own Makefiles and on Kconfig symbols being defined by sourced Kconfig files.

Risks: mismatched Kconfig symbol names would silently omit a driver family from builds. New MediaTek subtrees need corresponding `obj-*` entries.

Test signals: build a configuration with `CONFIG_MT7601U=m/y` and `CONFIG_MT76_CORE=m/y` and verify kbuild descends into the expected directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/Kconfig

Purpose: defines core mt76 Kconfig symbols and sources per-chip mt76 family configuration. It separates shared core, transport, library, LED, NPU, and chipset-specific options.

Important APIs/types/functions: defines `MT76_CORE` as a hidden tristate selecting `PAGE_POOL`; `MT76_LEDS` with LED class dependency and default; transport symbols `MT76_USB` and `MT76_SDIO`; shared library symbols `MT76x02_LIB`, `MT76x02_USB`, `MT76_CONNAC_LIB`, `MT792x_LIB`, `MT792x_USB`; and `MT76_NPU`. It sources Kconfig files for `mt76x0`, `mt76x2`, `mt7603`, `mt7615`, `mt7915`, `mt7921`, `mt7996`, and `mt7925`.

Control flow: chip-specific drivers select the shared library and transport symbols they need. Enabling a chip driver pulls in `MT76_CORE`, which in turn selects `PAGE_POOL`, making the common DMA/RX code available. Optional LED and NPU support are gated by their own symbols.

State and persistence: persists only through kernel configuration symbols. There is no runtime code in this file.

Dependencies and integration: integrated with kbuild through the sibling Makefile and with Linux subsystems through `PAGE_POOL`, `LEDS_CLASS`, PCI/USB/SDIO symbols in child Kconfigs, and optional NPU support.

Risks: hidden library symbols must be selected correctly by child drivers; otherwise builds can miss shared objects. The LED dependency expression must stay compatible with built-in/module combinations. Adding a new chipset requires sourcing its Kconfig and adding Makefile object rules.

Test signals: configuration tests should cover built-in and module combinations for core, LED class, USB/SDIO transport, NPU, and each sourced chipset family. Kconfig linting should catch unmet dependency chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/Makefile

Purpose: defines kbuild composition for the mt76 common module, transport modules, shared chipset libraries, and per-chip subdirectories.

Important APIs/types/functions: builds `mt76.o`, `mt76-usb.o`, `mt76-sdio.o`, `mt76x02-lib.o`, `mt76x02-usb.o`, `mt76-connac-lib.o`, `mt792x-lib.o`, and `mt792x-usb.o` from symbol-dependent object lists. The core `mt76-y` list includes `mmio.o`, `util.o`, `trace.o`, `dma.o`, `mac80211.o`, `debugfs.o`, `eeprom.o`, `tx.o`, `agg-rx.o`, `mcu.o`, `wed.o`, `scan.o`, and `channel.o`. Optional objects include `npu.o`, `pci.o`, and `testmode.o`. Trace CFLAGS add `-I$(src)`.

Control flow: kbuild expands object lists based on enabled Kconfig symbols, compiles shared objects into their module archives, and descends into chip subdirectories for enabled chip families. Transport and library modules can be selected independently by chipset drivers.

State and persistence: no runtime state. Build outputs are object files/modules shaped by this file.

Dependencies and integration: depends on the Kconfig symbols defined in `mt76/Kconfig` and child Kconfigs. Integrates with Linux kbuild syntax for composite modules and conditional object inclusion.

Risks: object list order matters for link-time symbol resolution and initialization dependencies. Missing a shared source file from `mt76-y` can produce unresolved symbols in chip drivers; including optional code without the matching config can break builds. Trace include flags must track generated trace headers.

Test signals: allmodconfig and representative built-in/module builds should verify each composite module links, trace sources find headers, optional NPU/PCI/testmode objects are included only when intended, and all child subdirectories build under their symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/agg-rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/agg-rx.c

Purpose: implements mt76 software RX BlockAck reorder buffering. It accepts received skbs with mt76 RX metadata, buffers out-of-order aggregated frames per WCID/TID, releases in-order frames to mac80211, handles BAR control frames, and tears down reorder state when BA sessions stop.

Important APIs/functions: exports `mt76_rx_aggr_reorder`, `mt76_rx_aggr_start`, and `mt76_rx_aggr_stop`. Internal helpers include `mt76_aggr_tid_to_timeo`, `mt76_aggr_release`, `mt76_rx_aggr_release_frames`, `mt76_rx_aggr_release_head`, `mt76_rx_aggr_check_release`, `mt76_rx_aggr_reorder_work`, `mt76_rx_aggr_check_ctl`, and `mt76_rx_aggr_shutdown`.

Control flow: `mt76_rx_aggr_start` first stops any existing TID session, allocates a flexible `mt76_rx_tid` with a `reorder_buf[]`, initializes head sequence/size/work/lock, and publishes it through RCU. `mt76_rx_aggr_reorder` initially queues the skb for completion, finds the station and TID, ignores non-aggregated/no-ack traffic, and locks the TID. Frames older than the head are dropped, the first acceptable frame starts the session, in-order frames advance `head` and release contiguous buffered frames, while future frames are unlinked from completion and stored by sequence modulo window size. If a sequence lies outside the reorder window, older frames are released to make room. A delayed work item releases expired holes based on shorter VI timeout or longer BE/BK timeout. BAR frames release up to the requested start sequence. Stop removes the RCU pointer, marks the TID stopped, frees buffered skbs, cancels delayed work, and frees via RCU.

State and persistence: per-WCID `wcid->aggr[tid]` RCU pointers hold active `mt76_rx_tid` state: head sequence number, reorder window size, TID number, started/stopped flags, `nframes`, spinlock, delayed work, and buffered skb pointers. Per-skb `struct mt76_rx_status` carries `seqno`, `qos_ctl`, `aggr`, `wcid`, flags, and `reorder_time`. State is runtime only and reset when BA sessions stop.

Dependencies and integration: depends on mt76 core metadata, Linux sk_buff queues, RCU, spinlocks, delayed work, mac80211 sequence helpers, BAR frame formats, and `mt76_rx_complete`. It is called from mt76 RX paths before final mac80211 completion.

Risks: sequence arithmetic and modulo indexing must respect the negotiated reorder window to avoid retaining wrong frames or dropping valid ones. RCU publication/removal requires callers to hold the documented device mutex for `rcu_replace_pointer` lockdep. Work cancellation must happen after marking stopped to prevent requeue races. Duplicate slot detection drops the new skb. Delayed release trades latency against reordering; wrong timeout choices can harm throughput or voice/video latency.

Test signals: test BA start/stop, in-order AMPDU, out-of-order holes, duplicate sequence numbers, sequence wraparound, BAR-triggered release, timeout release, no-ack frames, non-aggregated control frames, station removal during pending work, and memory accounting for buffered skbs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/agg-rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/channel.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/channel.c

Purpose: implements common mt76 mac80211 channel context, multi-link virtual-interface link assignment, and remain-on-channel helpers. It maps chanctx objects to the correct mt76 PHY, updates hardware channel state, creates temporary offchannel links when needed, and completes or aborts ROC operations.

Important APIs/functions: exports `mt76_add_chanctx`, `mt76_remove_chanctx`, `mt76_change_chanctx`, `mt76_assign_vif_chanctx`, `mt76_unassign_vif_chanctx`, `mt76_switch_vif_chanctx`, `mt76_abort_roc`, `mt76_remain_on_channel`, and `mt76_cancel_remain_on_channel`. Other shared helpers include `mt76_get_vif_phy_link`, `mt76_put_vif_phy_link`, `mt76_roc_complete`, and `mt76_roc_complete_work`.

Control flow: chanctx add selects the band PHY, aborts scans on that PHY, and if the PHY has no active context updates `radar_enabled`, `main_chandef`, `chanctx`, and calls `__mt76_set_channel`. Chanctx change handles width/radar changes by aborting ROC, cancelling MAC work, and updating channel under the device mutex. VIF assignment aborts scans, allocates a per-link `mt76_vif_link` if needed, sets its context, and calls the driver `vif_link_add`; unassignment calls `vif_link_remove` and clears context. Context switching can move links between PHYs, remove/add link state, update channel, then rewrite each link's context and beacon monitor timestamp. Remain-on-channel finds the band PHY, rejects concurrent ROC/scan/reset, creates or reuses a link, marks ROC state, switches channel with offchannel notification if needed, notifies mac80211 ready, and schedules delayed completion. Completion restores the main channel, sends offchannel expiry, removes temporary links, and clears ROC state.

State and persistence: state is runtime in `struct mt76_phy` (`chanctx`, `main_chandef`, `radar_enabled`, `roc_vif`, `roc_link`, `offchannel`), `struct mt76_chanctx` (`phy`), `struct mt76_vif_data` (`link[]`, `offchannel_link`, `roc_phy`), and per-link `struct mt76_vif_link` (`ctx`, `offchannel`, beacon monitor fields). RCU pointers publish extra MLO/offchannel links.

Dependencies and integration: depends on mac80211 chanctx/MLO/ROC APIs, mt76 driver callbacks `vif_link_add` and `vif_link_remove`, scan/ROC abort helpers, `__mt76_set_channel`, offchannel notification helpers, delayed work, RCU, and the global mt76 device mutex.

Risks: link allocation and driver callback failure paths must free only newly allocated links and avoid leaving RCU pointers stale. Moving links between PHYs in `mt76_switch_vif_chanctx` can partially remove/add links if a later add fails; callers need hardware-specific rollback behavior or acceptance of mac80211 retry. ROC completion is called from work and abort paths and must avoid double-completing when reset is active. Monitor interfaces with zero address intentionally bypass link setup. Correct mutex/RCU use is required for MLO link arrays.

Test signals: cover adding/removing/changing chanctx on both bands, switching contexts across PHYs, assigning/unassigning default and non-default MLO links, monitor zero-address vif behavior, scan abort interactions, ROC success/cancel/timeout, ROC during MCU reset, offchannel temporary link allocation failure, and beacon monitor timestamp updates after channel switch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/channel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/debugfs.c

Purpose: provides common mt76 debugfs helpers for register access, queue inspection, NAPI threading control, EEPROM/OTP blobs, and formatted diagnostic arrays.

Important APIs/functions: exports `mt76_queues_read`, `mt76_seq_puts_array`, and `mt76_register_debugfs_fops`. Internal debugfs accessors implement `regval` read/write through `__mt76_rr/__mt76_wr`, `napi_threaded` get/set through `dev_set_threaded`, and RX queue status via a seqfile.

Control flow: driver code calls `mt76_register_debugfs_fops` with a PHY and optional register fops. The helper creates an `mt76` directory under the wiphy debugfs dir, exposes `led_pin`, `regidx`, `regval`, `napi_threaded`, `eeprom`, optional `otp`, and `rx-queues`. The queue readers print head/tail/queued values for TX and RX queues; RX queue displayed queued count is adjusted for USB because its software/hardware accounting is inverted.

State and persistence: debugfs files expose mutable runtime fields such as `dev->debugfs_reg`, `phy->leds.pin`, and `dev->napi_dev->threaded`. EEPROM and OTP are exposed as read-only blobs backed by driver memory. Changes do not persist across driver reload except where hardware/EEPROM data is inherently persistent.

Dependencies and integration: depends on Linux debugfs, seq_file, dummy netdev NAPI state, mt76 register accessors, queue structures, and wiphy debugfs directories. Chip drivers can reuse queue readers in their own debugfs files.

Risks: `regval` is raw register access; writing arbitrary addresses can disturb hardware and should remain privileged debugfs. `napi_threaded` supports MMIO only and returns `-EOPNOTSUPP` otherwise. `debugfs_create_file_unsafe` assumes debugfs lifetime is tied to device cleanup. Queue snapshots are not globally locked and are diagnostic rather than transactional.

Test signals: verify debugfs directory creation for each PHY, register read/write using `regidx/regval`, NAPI threaded toggling on MMIO and rejection on non-MMIO, EEPROM/OTP blob readability, and queue readers under active traffic without crashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/dma.c

Purpose: implements common mt76 DMA queue operations for MMIO-style devices, including TXWI/RXWI caches, TX descriptor construction and cleanup, RX page-pool refill and NAPI polling, WED/RRO/NPU queue variants, queue allocation/reset, and global DMA teardown.

Important APIs/functions: exported functions are `mt76_get_rxwi`, `mt76_put_txwi`, `mt76_put_rxwi`, `mt76_free_pending_rxwi`, `mt76_dma_rx_fill`, `mt76_dma_rx_poll`, `mt76_dma_attach`, and `mt76_dma_cleanup`. The `mt76_dma_ops` table provides queue ops: `init`, `alloc`, `reset_q`, `tx_queue_skb_raw`, `tx_queue_skb`, `tx_cleanup`, `rx_queue_init`, `rx_cleanup`, `rx_reset`, and `kick`. Internal helpers allocate/free TXWI/RXWI cache entries, reset/sync queue indices, add TX/RX buffers, dequeue RX buffers, process RX fragments, and cleanup TX descriptors.

Control flow: attach installs DMA queue ops. Queue allocation initializes locks, register pointers, descriptor memory, queue entries, page pool, optional NPU/WED setup, and resets indices/descriptors unless the queue type requires hardware-specific setup. TX skb path checks reset state and queue space, obtains a DMA-mapped TXWI, maps skb head/frags, lets the chip driver fill TXWI via `tx_prepare_skb`, adds descriptors two buffers at a time, and kicks the queue. TX cleanup reads hardware DMA index unless flushing, unmaps descriptor buffers, runs NPU descriptor cleanup, reports completion, returns TXWI to cache, resets indices on flush, and wakes `tx_wait` when empty. RX refill allocates page-pool buffers or special RRO descriptors, maps tokens for WED RX, fills descriptors, and kicks hardware. RX NAPI processing dequeues completed descriptors, handles RRO indication/rxdmad magic counters, resolves WED RX tokens, drops PN/repeat/old packets according to descriptor bits, builds skbs with page recycling, assembles multi-fragment frames via `q->rx_head`, calls optional `rx_check`, and hands completed frames to the chip driver `rx_skb`. Cleanup disables workers/NAPI, flushes all TX queues, removes RX NAPI, drains RX queues, destroys page pools, detaches WED devices, frees caches, and releases dummy netdevs.

State and persistence: runtime queue state includes descriptor rings, DMA addresses, queue entries, head/tail/queued counters, magic counters, RX fragment head, page pools, TXWI/RXWI cache lists, WED/NPU flags/registers, NAPI dummy netdevs, and completion waiters. DMA coherent descriptors persist for the device lifetime; page-pool buffers and TXWI caches are recycled until cleanup. No disk persistence exists.

Dependencies and integration: depends on Linux DMA mapping, page_pool, NAPI, sk_buff fragments, mt76 queue/token helpers, mt76 chip-driver callbacks (`tx_prepare_skb`, `rx_skb`, `rx_check`, RRO callbacks), optional MediaTek WED, optional MT76_NPU/Airoha NPU, and `mt76_connac` definitions. It is the common queue backend selected by `mt76_dma_attach`.

Risks: descriptor ownership, DMA sync direction, skip-unmap flags, and multi-buffer descriptor packing are correctness-critical; mistakes can cause DMA leaks, use-after-free, or corrupt frames. WED/RRO/NPU special queues have alternate descriptors and magic counters, so generic cleanup/refill must branch exactly. RX fragment assembly must drop oversized or excessive-fragment packets without leaking page-pool buffers. TX overflow error paths must unmap all mapped buffers and report TX status to keep mac80211 accounting correct. Cleanup assumes NAPI/workers are stopped before destroying page pools and caches. In the NPU `Q_READ/Q_WRITE` macros from the header, references must match the queue variable name expected by macro expansion.

Test signals: stress TX with fragmented and linear skbs, queue full and reset paths, raw MCU TX, DMA mapping failures, WED RX token allocation/release, RRO indication/rxdmad queues, PN/drop/repeat/old packet handling, RX multi-fragment frames, RX refill under memory pressure, NAPI budget completion, NPU-active TX/RX, flush cleanup during reset, page-pool leak detection, and allmodconfig builds with/without WED/NPU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/dma.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/dma.h

Purpose: declares mt76 DMA descriptor formats, bitfield definitions, queue register access macros, WED/RRO/NPU descriptor helpers, queue operation prototypes, and small inline helpers shared by `dma.c` and hardware-specific mt76 drivers.

Important APIs/types/functions: defines descriptor bit masks such as `MT_DMA_CTL_SD_LEN*`, `MT_DMA_CTL_LAST_SEC*`, `MT_DMA_CTL_DMA_DONE`, token/drop/PN/RRO fields, header lengths, `struct mt76_desc`, `struct mt76_wed_rro_desc`, `struct mt76_rro_rxdmad_c`, `enum mt76_qsel`, `enum mt76_mcu_evt_type`, and `enum mt76_dma_wed_ind_reason`. Declares `mt76_dma_rx_poll`, `mt76_dma_attach`, `mt76_dma_cleanup`, `mt76_dma_rx_fill`, and `mt76_dma_queue_reset`. Provides inline `mt76_dma_reset_tx_queue`, `mt76_dma_should_drop_buf`, and `mt76_priv`.

Control flow: `Q_READ` and `Q_WRITE` abstract queue register access across plain MMIO, WED-backed queues, and optional NPU queues. `mt76_dma_reset_tx_queue` delegates to queue ops, then redoes WED DMA setup if active. `mt76_dma_should_drop_buf` decodes descriptor drop state, including newer descriptor version behavior for WED indication reasons and PN check failures. `mt76_priv` maps a dummy NAPI netdev back to its owning `mt76_dev`.

State and persistence: no independent state; structures describe coherent DMA descriptors and helper functions inspect queue/device state. Drop decisions are derived from descriptor `ctrl`, `buf1`, and `info` values produced by hardware.

Dependencies and integration: depends on Linux bitfield macros, MMIO accessors, optional `CONFIG_NET_MEDIATEK_SOC_WED`, optional `CONFIG_MT76_NPU`, RCU/regmap for NPU register access, mt76 queue flags, WED setup helpers, and netdev private storage. It is tightly coupled to `dma.c` descriptor programming.

Risks: bit definitions are hardware ABI; wrong masks corrupt descriptor programming. `Q_READ/Q_WRITE` macro branches must use the correct queue variable and are sensitive to compile-time config combinations. Drop logic changes receive semantics for repeat/old/PN-fail packets; errors can either leak bad frames upward or drop valid fragments. `DMA_DUMMY_DATA` uses an invalid pointer sentinel and must never be dereferenced.

Test signals: compile with WED enabled, NPU enabled, and neither enabled; validate descriptor bit encoding in TX/RX paths; exercise `mt76_dma_should_drop_buf` cases for normal, repeat, old packet with/without fragment, PN failure, and legacy descriptor versions; verify dummy netdev private lookup during NAPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/dma.h -->
