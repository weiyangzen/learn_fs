# Research: subset-b-004772

Grouped source research for ath9k PCI/mac80211 initialization, reset, MAC, MCI coexistence, PCI bus, PHY constants, and receive processing. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/init.c

Purpose: Initializes and tears down the ath9k softc and module, binding Atheros 802.11n hardware to mac80211 across PCI/AHB buses. It owns module parameters, DMI MSI quirks, register access serialization, EEPROM/NVMEM/OF calibration loading, descriptor DMA allocation, hardware capability publication, mac80211 registration, debug/LED/rfkill startup, and staged deinitialization.

Important APIs and functions: Public entry points are `ath_descdma_setup()`, `ath9k_init_device()`, and `ath9k_deinit_device()`. Internal helpers include `ath9k_ioread32()`, `ath9k_iowrite32()`, `ath9k_reg_rmw()`, `ath9k_reg_notifier()`, `ath9k_init_softc()`, `ath9k_set_hw_capab()`, `ath9k_init_txpower_limits()`, `ath9k_of_init()`, `ath9k_nvmem_request_eeprom()`, and module hooks `ath9k_init()`/`ath9k_exit()`.

Control flow: Module init registers PCI, then AHB, then applies DMI quirks. Device init allocates `struct ath_hw`, wires ath common ops and power-save ops, parses platform/OF/NVMEM calibration, initializes locks, tasklets, timers, work items, channel contexts, hardware, TX queues, BT coexistence, channels/rates, crypto, P2P/offchannel state, and ASPM. `ath9k_init_device()` then sets mac80211 capabilities, regulatory hooks, TX/RX DMA, TX power, LEDs, registers `ieee80211_hw`, debugfs, regulatory hints, LEDs, and rfkill polling. Error paths unwind RX, registration, queues, hardware, EEPROM, and allocated SKBs.

State and persistence: Mutates module globals such as `ath9k_use_msi`, `ath9k_modparam_nohwcrypt`, `ath9k_btcoex_enable`, and `is_ath9k_unloaded`; runtime softc state such as `sc->sc_ah`, locks, timers, `cur_chan`, `tx99_power`, beacon slots, antenna diversity, spectral config, and mac80211 capabilities; and hardware/NVMEM/firmware calibration pointers. Persistent inputs are EEPROM, NVMEM calibration cells, firmware EEPROM blobs, OF MAC address, DMI quirks, and PCI subsystem driver data.

Dependencies and integration points: Depends on Linux DMA, firmware, NVMEM, OF, DMI, relay/debug, cfg80211/mac80211, ath common regulatory/rate/crypto helpers, PCI/AHB bus registration, RX/TX setup, BTCOEX, P2P, WOW, LED, rfkill, and DFS detector infrastructure. Register ops become `common->ops` and are consumed by low-level `ath9k_hw_*` code.

Risks: Register serialization is chipset-sensitive; missing `sc_serial_rw` protection can corrupt PCI register FIFO accesses. DMA descriptor allocation must avoid 4 KiB split transactions on older hardware. Firmware/NVMEM calibration length and byte-swap flags determine radio correctness. Capability flags exposed to mac80211 must match hardware features. Error unwinds must not double release devres-managed memory or leak firmware blobs. DMI/MSI and PCOEM quirks are hardware-specific.

Test signals: Probe/remove with PCI and AHB builds, OF no-eeprom firmware path, NVMEM calibration path, invalid calibration sizes, DMI MSI systems, PCOEM subsystem quirks, TX/RX DMA allocation failures, regulatory changes updating TX power/DFS detector, mac80211 registration failure unwinds, LED/rfkill/debugfs lifecycle, and module unload setting `is_ath9k_unloaded`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/link.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/link.c

Purpose: Provides ath9k runtime health monitoring, reset triggers, PLL workaround polling, PAPRD calibration, ANI/noise calibration, and survey counter maintenance. It is the link-maintenance layer that keeps the radio usable after TX/RX hangs, calibration failures, or changing channel/noise conditions.

Important APIs and functions: Public functions include `ath_hw_check_work()`, `ath_hw_check()`, `ath_hw_pll_work()`, `ath_paprd_calibrate()`, `ath_ani_calibrate()`, `ath_start_ani()`, `ath_stop_ani()`, `ath_check_ani()`, `ath_update_survey_nf()`, and `ath_update_survey_stats()`. Key helpers are `ath_tx_complete_check()`, `ath_hw_rx_inactive_check()`, `ath_hw_pll_rx_hang_check()`, `ath_paprd_send_frame()`, and `ath_paprd_activate()`.

Control flow: `hw_check_work` runs periodically and stops rescheduling if MAC alive checks, TX completion checks, or RX activity checks queue a reset. TX hang detection marks active AC queues as in progress on one pass and resets if they remain stuck on a later pass. RX inactivity expects at least roughly one interrupt per second over a four-second interval. PLL work runs only after beaconing/association and queues a reset after repeated bad PLL sums. ANI timer runs only when hardware is awake; it schedules long/short calibration and ANI monitor work, updates survey counters, queues resets on calibration failure, and reschedules itself at the shortest needed interval. PAPRD work sends training frames and activates per-chain predistortion tables once calibration succeeds.

State and persistence: Mutates queue `axq_tx_inprogress`, `rx_active_count`, `rx_active_check_time`, reset counters, `common->ani` timers and `caldone`, `PS_WAIT_FOR_ANI`, survey time/busy/RX/TX/noise fields, channel calibration flags such as `PAPRD_DONE`, and `ah->paprd_table_write_done`. All state is runtime-only but directly affects future reset, rate/noise, and power-save behavior.

Dependencies and integration points: Integrates with `ath9k_queue_reset()` in `main.c`, TX queue locks, `ath9k_hw_check_alive()`, AR9003 PLL/PAPRD helpers, mac80211 workqueue/timer APIs, power-save wake/restore, `ath9k_hw_calibrate()`, ANI monitor functions, survey reporting through `get_survey`, and common cycle counters.

Risks: False hang detection can cause disruptive resets under low traffic or delayed interrupts. The PLL hang counter is static, so behavior is shared across calls and assumes one active device context. ANI must not touch hardware while asleep except by setting wait flags. PAPRD reuses a single training skb across chains and relies on completion timing from TX completion. Survey math depends on clockrate and counter resets.

Test signals: Simulate TX queue hang, RX inactivity, MAC hang, PLL hang, and calibration failure reset types; verify ANI starts/stops with AP/STA/IBSS beacon state; inspect survey busy/noise updates; exercise PAPRD success, timeout, retrain, and activation paths; validate no work reschedules after a queued reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mac.c

Purpose: Implements exported low-level MAC helper APIs for ath9k queue control, TX/RX descriptor processing, DMA stop/abort, beacon queue setup, interrupt programming, and TX filtering. It bridges driver logic to Atheros AR register programming.

Important APIs and functions: Exports `ath9k_hw_gettxbuf()`, `ath9k_hw_puttxbuf()`, `ath9k_hw_txstart()`, `ath9k_hw_numtxpending()`, `ath9k_hw_updatetxtriglevel()`, `ath9k_hw_abort_tx_dma()`, `ath9k_hw_stop_dma_queue()`, `ath9k_hw_set_txq_props()`, `ath9k_hw_get_txq_props()`, `ath9k_hw_setuptxqueue()`, `ath9k_hw_releasetxqueue()`, `ath9k_hw_resettxqueue()`, `ath9k_hw_rxprocdesc()`, `ath9k_hw_setrxabort()`, `ath9k_hw_putrxbuf()`, `ath9k_hw_startpcureceive()`, `ath9k_hw_abortpcurecv()`, `ath9k_hw_stopdmarecv()`, `ath9k_hw_beaconq_setup()`, `ath9k_hw_intrpend()`, interrupt enable/disable helpers, and `ath9k_hw_set_tx_filter()`.

Control flow: TX queue setup maps abstract queue types to QCU IDs, stores properties, and resets queues by programming contention windows, AIFS, retry limits, CBR/ready time, burst time, beacon/CAB/UAPSD-specific flags, descriptor CRC checks, and interrupt masks. TX abort/stop assert queue disable or forced channel-idle bits and poll pending counters. RX descriptor processing converts hardware status words into `ath_rx_status`, handling RSSI, rate, aggregation, key index, delimiter CRC, PHY/CRC/decrypt/MIC/keymiss errors, STBC/GI/bandwidth flags, and corrupt descriptor detection. Interrupt setup derives AR_IMR/S2/S5 and MSI masks from `ah->imask`, queue interrupt masks, mitigation settings, autosleep, MCI, and BB watchdog config.

State and persistence: Mutates `ah->txq[]`, queue interrupt masks, `ah->imrs2_reg`, `ah->msi_mask`, `ah->msi_reg`, `ah->intr_ref_cnt`, `ah->tx_trig_level`, and hardware registers. No durable persistence exists, but register state persists until reset or reprogramming and must match in-memory masks.

Dependencies and integration points: Depends on `hw.h`, `hw-ops.h`, AR register macros, revision predicates, atomic interrupt reference counting, and exported symbols used by TX, RX, main interrupt/reset code, beaconing, and station power-save filtering.

Risks: Register bitfield mistakes directly corrupt queue timing, interrupt delivery, or descriptor interpretation. Interrupt reference count imbalance can leave interrupts disabled or spuriously enabled. RX status error precedence intentionally treats errors as mutually exclusive; changes can alter drop/stat behavior. DMA stop polling has hardware-specific stuck-state handling. MSI enable loops and masks are revision-sensitive.

Test signals: Configure all queue types, WMM AC parameter changes, beacon/CAB behavior, TX underrun trigger-level increases, TX DMA stop timeout, RX descriptor parsing for OK/PHY/CRC/decrypt/MIC/keymiss/corrupt cases, RX abort idle timeout, interrupt mask transitions with MSI and legacy INTx, MCI interrupt enabling, and sleeping-station TX filter programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mac.h

Purpose: Defines the ath9k MAC descriptor/status ABI, TX/RX bitfields, queue/filter/key enums, 802.11n rate-series helper macros, and prototypes for MAC helper functions. It is the shared contract between descriptor construction/parsing code, TX/RX paths, and hardware-specific MAC implementations.

Important APIs and types: Major types are `struct ath_tx_status`, `struct ath_rx_status`, `struct ath_htc_rx_status`, packed `struct ath_desc`, packed `struct ar5416_desc`, `enum ath9k_phyerr`, `enum ath9k_tx_queue`, `enum ath9k_tx_queue_flags`, `struct ath9k_tx_queue_info`, `enum ath9k_rx_filter`, `struct ath9k_11n_rate_series`, `enum aggr_type`, `enum ath9k_key_type`, and `struct ath_tx_info`. It declares all exported MAC helpers implemented in `mac.c` plus `ath9k_hw_setuprxdesc()` and `ar9002_hw_attach_mac_ops()`.

Control flow: The header has no runtime flow, but its macros drive how callers populate multi-rate TX descriptors (`set11nTries`, `set11nRate`, `set11nPktDurRTSCTS`, `set11nRateFlags`, `set11nChainSel`) and decode AR5416 descriptor status words. Queue flags and RX filter bits are consumed by queue setup, RX filter calculation, interrupt selection, and mac80211 callback handling.

State and persistence: Owns no state. Its packed descriptor layout and constants define hardware-visible DMA memory format and driver-visible status memory format. Any ABI drift affects descriptors already allocated and status parsing across the driver.

Dependencies and integration points: Includes cfg80211 rate/bandwidth definitions and depends on AR register bit macros from lower ath9k headers. It is included by MAC, TX, RX, hardware ops, and chipset attachment code. `ath_rx_status` maps directly into mac80211 `ieee80211_rx_status`; `ath_tx_info` maps software TX metadata into hardware descriptor programming.

Risks: Incorrect bit masks, shifts, packing, or alignment cause hardware DMA corruption or bad status interpretation. `ATH9K_TXQ_USEDEFAULT` as `(u32)-1` requires careful comparisons. Descriptor comments document interrupt moderation tradeoffs; over-deferred TX interrupts can stale rate control and backup senders. `struct_group(ba, ...)` exposes block-ack bitmap fields as a unit and must stay layout-compatible.

Test signals: Compile coverage across AR9002/AR9003, descriptor size/alignment assertions, TX descriptor setup/parse tests, RX status parse tests, queue flag programming, RX filter combinations, key type use with crypto setup, and sparse/endian checks for HTC big-endian RX status fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/main.c

Purpose: Main mac80211-facing ath9k runtime implementation. It provides power-save reference counting, reset orchestration, interrupt/tasklet processing, TX entry, interface/station/key/beacon state management, configuration callbacks, survey/stat reporting, channel-context/offchannel support, antenna control, flushing, and the final `ieee80211_ops` table.

Important APIs and functions: Exported or shared functions include `ath9k_parse_mpdudensity()`, `ath_ps_full_sleep()`, `ath9k_ps_wakeup()`, `ath9k_ps_restore()`, `ath_cancel_work()`, `ath_restart_work()`, `ath9k_tasklet()`, `ath_isr()`, `ath_reset()`, `ath9k_queue_reset()`, `ath_reset_work()`, `ath9k_calculate_iter_data()`, `ath9k_calculate_summary_state()`, `ath9k_set_txpower()`, `__ath9k_flush()`, and `ath9k_fill_chanctx_ops()`. Static mac80211 callbacks include start/stop/tx/config/filter/station/key/BSS/TSF/A-MPDU/survey/coverage/flush/scan/channel-context operations.

Control flow: ISR rejects invalid/shared interrupts, reads and masks ISR status, caches it in `sc->intrstatus`, handles immediate beacon/TX underrun/TIM_TIMER bits, kills interrupts, and schedules tasklets for substantive work. `ath9k_tasklet()` handles fatal/BB/GTT reset triggers, RX high/low priority processing, TX completions, generic timers, BTCOEX, and interrupt resume under PCU lock and PS wake. Reset flow disables work, IRQ, tasklets, interrupts, ANI, RX/TX DMA, resets hardware, recalculates summary state, restarts RX/beacons/work/TX scheduling, restores interrupt masks, and wakes queues. mac80211 start performs initial reset and interrupt mask setup; stop cancels work, disables interrupts, drains RX/TX, resets/phy-disables hardware, clears keys, and marks invalid.

State and persistence: Manages `common->op_flags`, `ah->imask`, `ps_usecount`, `ps_idle`, `ps_enabled`, `ps_flags`, `gtt_cnt`, `intrstatus`, key pending maps, `cur_chan`/channel contexts, beacon slots, station private state, TX queues, survey state, chain masks, offchannel scheduler state, LED GPIO state, and TSF snapshots. No durable persistence, but mac80211-visible state and hardware register state must remain synchronized.

Dependencies and integration points: Integrates with mac80211/cfg80211 operations, TX/RX tasklets, `ath9k_hw_*` low-level ops, ANI/link work, beacon, BTCOEX/MCI, dynack, P2P/offchannel/channel-context helpers, WOW/debugfs, crypto key cache, airtime/survey APIs, and PCI IRQ lifecycle.

Risks: Reset sequencing is lock-sensitive and mixes IRQ disable, tasklet disable, mutexes, spinlocks, and power-save references. Interrupt masks must not be re-enabled during invalid/stop/reset states. Key deletion is delayed while queued frames reference key cache entries. PS flags gate when hardware may sleep; wrong transitions drop ACKs, beacons, or CAB/PS-Poll data. Channel-context code can race offchannel scan/ROC cancellation and queue assignment. `ath9k_set_key()` flushes outgoing PTKs to avoid encryption with wrong keys.

Test signals: Start/stop/open/close cycles, suspend-like idle transitions, fatal/BB/GTT/TX/RX reset paths, shared IRQ handling, EDMA and legacy RX/TX tasklets, PS nullfunc/PS-Poll/CAB/beacon sync, station sleep/awake filtering, pairwise key disable with queued frames, AP/STA/mesh/IBSS/OCB interface changes, A-MPDU actions, survey reads, flush with and without MCC timeout override, HW scan/ROC/channel-context operations, antenna mask validation, and TX power reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mci.c

Purpose: Implements AR9003 MCI Bluetooth coexistence policy for ath9k. It tracks BT profile/status messages, manages DMA-backed MCI scheduler/GPM buffers, updates WLAN/BT duty cycle and aggregation limits, sets coexistence TX priorities, handles MCI interrupts/messages, updates WLAN channel maps, and adjusts concurrent TX power behavior based on RSSI.

Important APIs and functions: Public entry points are `ath_mci_flush_profile()`, `ath_mci_setup()`, `ath_mci_cleanup()`, `ath_mci_intr()`, `ath_mci_enable()`, `ath9k_mci_update_wlan_channels()`, `ath9k_mci_set_txpower()`, and `ath9k_mci_update_rssi()`. Internal helpers include profile add/delete/find, `ath_mci_update_scheme()`, `ath_mci_cal_msg()`, `ath_mci_process_profile()`, `ath_mci_process_status()`, `ath_mci_msg()`, `ath_mci_set_concur_txprio()`, and `ath9k_mci_stomp_audio()`.

Control flow: Setup allocates one coherent DMA region, splits it into scheduler and GPM buffers, fills reserved patterns, calls `ar9003_mci_setup()`, and initializes work. Interrupt handling reads MCI interrupt/status bits, handles wake/sleep/reset/recovery messages, walks GPM entries until no more data, dispatches calibration messages or coexistence-agent messages, recycles entries, and queues `mci_work` when profile/status changes require scheme recalculation. Scheme update derives duty cycle, BT period, stomp type, aggregation limit, no-stomp airtime, and BTCOEX timer state from active BT profile counts and channel band.

State and persistence: Mutates `sc->btcoex.mci` profile list, profile counters, status bitmap, management count, aggregation limit, voice priority, `btcoex` duty cycle/period/stomp/no-stomp/audio/RSSI counters, `ah->btcoex_hw.mci` BT state/config/channel maps/concurrent TX flag, and MCI DMA buffer descriptors. State is runtime-only and should be flushed after BT info reset or device teardown.

Dependencies and integration points: Depends on `mci.h`, `ar9003_mci.h`, ath9k BTCOEX timer/hardware helpers, `ath9k_queue_reset()` for calibration requests, mac80211 workqueue, channel definitions, RSSI statistics, and TX power limit recalculation. `main.c` enables MCI interrupts and calls channel/TX power updates around association/offchannel/reset state.

Risks: MCI interrupt context uses GFP_ATOMIC profile allocation and list mutation; allocation failures silently drop profiles. Profile counters must stay balanced across type changes and deletes. GPM parsing uses fixed offsets and assumes alignment of payload casts. Scheme tuning is 2.4 GHz-specific and must avoid enabling BTCOEX on 5 GHz. Concurrent TX power changes are tied to calibration channel boundaries and RSSI hysteresis.

Test signals: MCI setup allocation failure, GPM version/status/profile messages, profile add/delete/type-change overflow limits, management critical status count changes, calibration request/grant reset behavior, RX invalid header recovery, 2 GHz vs 5 GHz scheme selection, WLAN channel map masking for HT20/HT40+/HT40-, concurrent TX RSSI threshold switching, and cleanup after disable/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mci.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mci.h

Purpose: Defines ath9k MCI coexistence constants, channel-map/profile accounting macros, data structures, and public MCI APIs. It is the local contract between ath9k core code and AR9003 MCI Bluetooth coexistence implementation.

Important APIs and types: Constants size the scheduler and GPM DMA buffers, BT channel maps, duty cycle bounds, default aggregation limits, profile limits, and TX priority thresholds. Macros `MCI_GPM_SET_CHANNEL_BIT()` and `MCI_GPM_CLR_CHANNEL_BIT()` edit BT channel masks; `INC_PROF()`, `DEC_PROF()`, and `NUM_PROF()` maintain profile counters. Types include `struct ath_mci_profile_info`, `struct ath_mci_profile_status`, `struct ath_mci_profile`, `struct ath_mci_buf`, and `struct ath_mci_coex`. Public functions include setup/cleanup/intr/profile flush/RSSI update plus BTCOEX-gated inline stubs for `ath_mci_enable()`, `ath9k_mci_update_wlan_channels()`, and `ath9k_mci_set_txpower()`.

Control flow: The header itself has no runtime flow, but conditional compilation controls whether the main driver calls real MCI enable/channel/TX-power functions or no-op stubs when `CONFIG_ATH9K_BTCOEX_SUPPORT` is disabled.

State and persistence: Owns no global state. Its structs define runtime state stored under `sc->btcoex.mci` and `sc->mci_coex`, including profile lists, status bitmap, profile counters, aggregation limit, DMA virtual/physical addresses, and buffer lengths.

Dependencies and integration points: Includes `ar9003_mci.h` for hardware message offsets and state definitions. Used by `mci.c`, `ath9k.h` softc definitions, `main.c` MCI calls, and BTCOEX logic. The list and bitmap fields depend on Linux list/bitmap infrastructure through included driver headers.

Risks: Profile counter macros assume valid profile types and balanced increment/decrement calls; underflow would corrupt coexistence policy. Channel bit macros operate on byte offsets into a dword array and require correct BT channel bounds. Conditional stubs can hide missing BTCOEX functionality in builds without support. Buffer size constants must match AR9003 MCI hardware expectations.

Test signals: Build with and without `CONFIG_ATH9K_BTCOEX_SUPPORT`, profile counter transitions for each BT profile type, channel map bit set/clear bounds at channels 0 and 78, DMA buffer sizing against hardware setup, and callers compiling against both real and stubbed APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/mci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/pci.c

Purpose: Implements ath9k PCI bus binding, device ID/subsystem quirk matching, bus operations, PCI probe/remove, optional MSI, ASPM handling, EEPROM reads, suspend/resume PM, and PCI driver registration.

Important APIs and functions: Exposes `ath_pci_init()` and `ath_pci_exit()` to module init/exit. Static pieces include the large `ath_pci_id_table[]`, `ath_pci_read_cachesize()`, `ath_pci_eeprom_read()`, `ath_pci_aspm_init()`, `ath_pci_bus_ops`, `ath_pci_probe()`, `ath_pci_remove()`, `ath_pci_suspend()`, and `ath_pci_resume()`.

Control flow: Probe enables the PCI device with pcim, sets 32-bit coherent DMA, repairs cache line size and latency timer, enables bus mastering, disables PCI retry timeout, maps BAR0, fills channel-context ops, allocates `ieee80211_hw`, stores softc device/memory/driver-data, optionally enables MSI, requests IRQ with shared INTx or MSI flags, calls `ath9k_init_device()`, records MSI state, and logs hardware name/mem/IRQ. Failure unwinds IRQ and hardware allocation. Remove marks unplugged unless module unload is active, deinitializes ath9k, frees IRQ, and frees mac80211 hw. Suspend bypasses full PCI suspend for WOW, otherwise stops BTCOEX, disables hardware, cancels sleep timer, and forces full sleep. Resume reapplies retry-timeout workaround, ASPM init, and clears reset-power-on.

State and persistence: Uses PCI config space, BAR mappings, IRQ registration, `pci_drvdata`, `sc->driver_data`, `sc->irq`, `sc->mem`, `ah->msi_enabled`, `ah->msi_reg`, `ah->aspm_enabled`, `ah->config.aspm_l1_fix`, `AH_UNPLUGGED`, and PCI subsystem quirk flags. PCI config changes persist until device reset/resume reinitialization.

Dependencies and integration points: Integrates with Linux PCI/PM/MSI APIs, mac80211 hardware allocation, ath9k core init/deinit, `ath_isr()`, PCI EEPROM register access, ASPM capability helpers, DMI-driven `ath9k_use_msi`, and PCOEM driver-data handling in `init.c`.

Risks: The device table encodes many subsystem-specific workarounds; ordering matters because more-specific entries must match before generic IDs. MSI is enabled before `ath9k_init_device()` but `sc->sc_ah->msi_enabled` is set after init, so interrupt setup timing depends on when interrupts are enabled. PCI config retry-timeout and cacheline fixes are hardware stability workarounds. ASPM disable for BTCOEX must update both endpoint and parent link. Remove/unplug distinction affects later register access.

Test signals: Probe/remove for generic and subsystem IDs, MSI and INTx IRQ paths, request_irq failure, BAR map failure, ath9k init failure unwind, PCI EEPROM read timeout/success, ASPM enabled/disabled with BTCOEX and AR9285/AR9462, suspend/resume with and without WOW, hot-unplug setting `AH_UNPLUGGED`, and module PCI registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/phy.h

Purpose: Provides compact PHY register and bitfield constants used by ath9k hardware code, especially channel select math, TX gain/CLC fields, antenna swap/reduced-chain flags, chip ID, spur frequency fields, PLL registers, and antenna diversity LNA configuration values.

Important APIs and types: Macros include `CHANSEL_2G()`, `CHANSEL_5G()`, `AR_PHY_BASE`, `AR_PHY(n)`, TX power/gain masks and shifts, CLC table/register fields, `ANTSWAP_AB`, `REDUCE_CHAIN_0`, `REDUCE_CHAIN_1`, `AR_PHY_CHIP_ID`, spur frequency masks, `AR_PHY_PLL_CONTROL`, and `AR_PHY_PLL_MODE`. The only type is `enum ath9k_ant_div_comb_lna_conf`, enumerating LNA1/LNA2 combining modes.

Control flow: None. This header is a constant definition layer consumed by register-programming code in chipset-specific PHY, calibration, spur mitigation, channel, PLL, and antenna-diversity paths.

State and persistence: No state. The constants define hardware register addresses and bit meanings; writes using these constants persist in hardware registers until reset/reprogramming.

Dependencies and integration points: Included by ath9k hardware implementation files through shared headers. Integrates with channel frequency selection, AR PHY register addressing, calibration/tuning logic, and antenna diversity decisions that reference `ath9k_ant_div_comb_lna_conf`.

Risks: Incorrect channel select divisors or register masks can tune the radio to wrong frequencies or corrupt PHY calibration. The file is small but high impact because constants are trusted by low-level code without runtime validation. LNA enum ordering must match code and hardware expectations.

Test signals: Compile all chipset PHY code, validate 2 GHz/5 GHz channel programming, PLL control writes, spur mitigation fields, TX gain calibration, antenna-diversity LNA transitions, and hardware bring-up/regression on devices using reduced-chain or antenna-swap settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/recv.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/recv.c

Purpose: Implements ath9k receive setup, RX DMA buffer management for legacy and EDMA hardware, RX filter calculation, receive start/stop, power-save beacon/CAB/PS-Poll handling, descriptor consumption, frame validation/postprocessing, antenna diversity updates, AMPDU metadata, airtime accounting, and delivery to mac80211.

Important APIs and functions: Public entry points are `ath_rx_init()`, `ath_rx_cleanup()`, `ath_calcrxfilter()`, `ath_startrecv()`, `ath_stoprecv()`, and `ath_rx_tasklet()`. Important helpers include `ath_rx_buf_link()`, `ath_rx_edma_buf_link()`, `ath_rx_addbuffer_edma()`, `ath_rx_edma_cleanup()`, `ath_opmode_init()`, `ath_flushrecv()`, `ath_rx_ps_beacon()`, `ath_rx_ps()`, `ath_edma_get_next_rx_buf()`, `ath_get_next_rx_buf()`, `ath9k_rx_skb_preprocess()`, `ath9k_antenna_check()`, `ath9k_apply_ampdu_details()`, and `ath_rx_count_airtime()`.

Control flow: RX init sets `common->rx_bufsize`, allocates descriptors/SKBs and maps DMA; EDMA initializes HP/LP FIFOs and posts buffers directly. Start receive posts descriptors or EDMA buffers, enables RX DMA, programs filters/opmode/BSSID/multicast, and starts PCU receive. Stop aborts PCU receive, clears filters, stops DMA, flushes tasklets, and removes EDMA buffers or clears legacy link state. `ath_rx_tasklet()` repeatedly obtains completed buffers, preprocesses status/header, allocates and maps replacement SKBs before unmapping the completed frame, handles chained fragments, postprocesses accepted frames, updates PS/antenna/AMPDU/debug/airtime/dynack state, calls `ieee80211_rx()`, then requeues buffers and reenables RXEOL/RXORN interrupts.

State and persistence: Mutates RX lists/FIFOs, descriptor links, `rxlink`, `buf_hold`, `frag`, `discard_next`, `defant`, `rxotherant`, `ampdu_ref`, PS flags, RX statistics, `rx.num_pkts`, survey/airtime through mac80211, and hardware RX filters/DMA pointers. State is runtime-only but tightly coupled to DMA ownership and interrupt progress.

Dependencies and integration points: Depends on DMA APIs, SKB allocation, mac80211 RX status/delivery, `ath9k_hw_rxprocdesc()` and EDMA descriptor processing, DFS/spectral processing, common RX accept/rate/RSSI helpers, channel-context beacon events, power-save logic from `main.c`, antenna combining, dynack, and airtime fairness APIs.

Risks: DMA ownership ordering is critical: replacement buffers are mapped before completed buffers are unmapped and reused. Fragment handling drops too many fragments and uses `discard_next` for corrupted chained descriptors. RX length/status validation prevents buffer overrun and corrupt descriptor propagation. RX filter computation depends on opmode, monitor flags, DFS, channel contexts, dynack, and chipset revisions. EDMA corrupt descriptor handling skips an extra buffer. PS beacon/CAB logic determines when hardware may return to sleep.

Test signals: Legacy and EDMA RX initialization/cleanup failures, RX start/stop DMA timeout, filter combinations for STA/AP/monitor/DFS/dynack/multi-vif/scanning, PHY error routing to DFS/spectral, CRC/decrypt/MIC/keymiss handling via common accept path, corrupt descriptor and length rejection, chained fragment reconstruction and drop paths, OOM replacement SKB path, PS beacon DTIM/CAB/PS-Poll transitions, antenna diversity switching, AMPDU last/delimiter flags, airtime accounting, dynack ACK sampling, and RXEOL/RXORN reenable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/recv.c -->
