# Research Group subset-b-004855

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/phy.c

Purpose: Shared MT76x2 PHY calibration and transmit-power code used by the PCI/USB variants. It programs AGC, PA mode, tx delay, TSSI/DPD compensation, and channel gain behavior through mt76 register helpers and MCU calibration commands.

Important APIs: exported entry points include `mt76x2_apply_gain_adj`, `mt76x2_phy_set_txpower_regs`, `mt76x2_phy_set_txpower`, `mt76x2_configure_tx_delay`, `mt76x2_phy_tssi_compensate`, and `mt76x2_phy_update_channel_gain`. Internal helpers adjust high LNA gain, AGC gain, and compute the minimum non-zero rate power.

Control flow: channel setup callers first read EEPROM-derived power info, apply bandwidth deltas, clamp rate power to configured/SAR limits, derive per-chain target offsets, and program hardware with `mt76x02_phy_set_txpower`. Periodic calibration alternates between triggering TSSI measurement and consuming completion state from `MT_BBP(CORE, 34)`, optionally running DPD once.

State and persistence: all persistent inputs come from EEPROM-parsed calibration fields in `dev->cal` and current chandef/txpower configuration. Runtime state includes `tssi_comp_pending`, `tssi_cal_done`, `dpd_cal_done`, `agc_gain_cur`, `low_gain`, RSSI averages, and cached `rate_power`/target deltas.

Dependencies and integration: depends on mt76x02 PHY/EEPROM helpers, mac80211 band/channel definitions, MCU calibration functions, external PA/LNA capability detection, DFS AGC adjustments, and raw register access.

Risks: register constants are hardware-sensitive; incorrect per-chain delta math or EEPROM interpretation can violate regulatory power limits or degrade RF performance. The assignment of `target_power_delta[1]` subtracts chain 0 target power, which is worth regression attention. Calibration paths must avoid running on silent/radar-sensitive channels incorrectly.

Test signals: validate per-band txpower using regulatory/SAR scenarios, channel switches across 20/40/80 MHz, external PA/LNA boards, TSSI/DPD completion, DFS channels, and RSSI-driven gain transitions under weak and strong signal conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb.c

Purpose: Linux USB driver binding for MT76x2U devices. It declares USB IDs, allocates the mt76 device, performs USB initialization, validates ASIC revision, registers mac80211 hardware, and handles disconnect and power management.

Important APIs: `mt76x2u_probe`, `mt76x2u_disconnect`, `mt76x2u_suspend`, `mt76x2u_resume`, the `mt76x2u_driver` `usb_driver`, and the static `mt76_driver_ops` passed to `mt76_alloc_device`.

Control flow: probe gets and resets the USB device, stores interface data, initializes MCU and mt76 USB transport, reads `MT_ASIC_VERSION`, rejects non-MT76x2 ASICs, then calls `mt76x2u_register_device`. Failure unwinds queues, device memory, interface data, and USB refcount. Disconnect marks removal, unregisters mac80211, cleans hardware, and releases the USB device. Resume restarts RX and reinitializes hardware.

State and persistence: persistent matching comes from `MODULE_DEVICE_TABLE`; runtime state is the USB interface data pointer, `MT76_REMOVED`, initialized queues, firmware identity, and mac80211 registration state.

Dependencies and integration: integrates with USB core, module firmware declarations, mt76 USB helpers, mt76x02 common callbacks for TX/RX/station handling, and `mt76x2u_ops` from `usb_main.c`.

Risks: probe error unwinding must stay symmetric with later initialization changes. `usb_reset_device` can disturb composite devices if assumptions change. Resume calls full hardware init after RX resume, so firmware or register failures must leave queues safely stopped.

Test signals: plug/unplug supported IDs, unsupported ASIC rejection, suspend/resume and reset_resume, firmware-missing failures, queue cleanup after failed probe, and `lsusb`/dmesg ASIC revision reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_init.c

Purpose: Hardware bring-up and registration path for MT76x2U. It powers WLAN/RF blocks, reads EEPROM over USB vendor register space, loads firmware and MCU state, resets MAC tables, allocates USB queues, and registers the device with mac80211.

Important APIs: `mt76x2u_init_hardware`, `mt76x2u_register_device`, `mt76x2u_stop_hw`, and `mt76x2u_cleanup`. Internal helpers configure USB DMA, RF power patches, WLAN MTCMOS, and EEPROM extraction.

Control flow: initialization resets WLAN, powers both RF units, waits for MAC readiness, loads ROM patch/firmware, waits for DMA idle, initializes USB DMA, starts MCU radio state, resets MAC, sets MAC address and rx filter, clears WCID/shared-key tables, initializes beacon config, loads CR tables, configures PHY paths, then stops the MAC until mac80211 start. Registration layers mt76 device init, EEPROM init, MCU response buffer allocation, USB queue allocation, hardware init, VHT capability selection, mac80211 registration, debugfs, and txpower setup.

State and persistence: EEPROM bytes are copied into devm-allocated `mt76.eeprom.data`; `dev->mt76.rxfilter`, revision-dependent VHT capability, work items, queue allocation, and `MT76_STATE_INITIALIZED` are runtime state.

Dependencies and integration: depends on mt76 USB queue helpers, mt76x02 EEPROM/MAC/PHY helpers, USB MCU loader in `usb_mcu.c`, MAC reset/stop in `usb_mac.c`, and txpower helpers from `phy.c`.

Risks: bring-up is timing-sensitive and uses many magic vendor registers. EEPROM read size and endian handling must match hardware. Registration failure paths rely on `mt76x2u_cleanup` being safe before full initialization. Disabling RX bulk aggregation is a deliberate copy-avoidance tradeoff.

Test signals: firmware load success, MAC wait timeouts, EEPROM MAC address correctness, VHT-disabled revision behavior, table reset after reinit, interface start after stopped MAC, and cleanup on each injected failure point.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_mac.c

Purpose: USB-specific MAC reset, crystal trim, timing, and stop sequencing for MT76x2U devices.

Important APIs: `mt76x2u_mac_reset` and `mt76x2u_mac_stop`. Internal `mt76x2u_mac_fixup_xtal` interprets EEPROM crystal trim fields and programs XO/FCE/timing registers.

Control flow: reset enables WPDMA bits, initializes PBF limits and common MAC defaults, configures TX link, auto response, max length, WMM, clears MAC/BBP reset, disables coexistence for MT7612, enables CCA settings, disables ALC bit 31, then applies XTAL fixups. Stop temporarily removes RTS retry limit, disables ED CCA/40 MHz TX hold, polls USB TX DMA idle, waits TX page counts, disables MAC TX/RX, waits MAC idle, toggles BBP reset bits if needed, waits RX page counts and MAC RX idle, then waits USB RX DMA idle and restores RTS config.

State and persistence: persistent trim values come from EEPROM. Runtime state includes removed-device bit, TX/RX DMA busy state, queue page counters, MAC status, and restored RTS configuration.

Dependencies and integration: called during hardware init, channel switching, stop, cleanup, suspend/resume, and calibration. Uses common mt76x02 MAC init tables and raw mt76 register helpers.

Risks: stop loops are hardcoded polling sequences; too-short waits can leave DMA active, too-long waits can stall teardown. XTAL fallback values affect RF stability. The function returns success even after warning that MAC RX failed to stop, so callers need external recovery if hardware is wedged.

Test signals: repeated start/stop, channel switch under load, device removal during stop, suspend/resume, MT7612 coexistence behavior, and observation of no leaked URBs or stuck DMA after teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_main.c

Purpose: mac80211 operations table for MT76x2U. It starts/stops the USB MAC, handles channel changes and configuration updates, and wires common mt76x02 callbacks into mac80211.

Important APIs: `mt76x2u_ops`, `mt76x2u_start`, `mt76x2u_stop`, `mt76x2u_set_channel`, and `mt76x2u_config`.

Control flow: start calls common USB MAC start, queues periodic MAC work, and sets running state. Stop clears running, stops USB TX, and invokes hardware stop. Channel setting disables pre-TBTT, stops MAC, sets PHY channel, resets channel counters, resumes MAC, and re-enables pre-TBTT. Config handles monitor flag by toggling `MT_RX_FILTR_CFG_PROMISC`; power changes convert mac80211 dBm to half-dBm, apply SAR, adjust for 2-chain power, and if running reprogram txpower. Channel change updates survey state after releasing the driver mutex.

State and persistence: runtime state is `MT76_STATE_RUNNING`, rx filter bits, configured txpower, chandef, scheduled MAC work, and per-interface/mac80211 state held by common callbacks.

Dependencies and integration: depends on mac80211, mt76 core TX queueing, mt76x02 common interface/key/AMPDU/filter routines, USB PHY channel code, and `mt76_get_sar_power`.

Risks: monitor-mode logic is easy to invert because promiscuous filtering is toggled from `hw->conf.flags`. Channel switch must preserve MAC stop/resume symmetry even when PHY set fails. Power adjustment assumes 2x2 devices and subtracts 6 half-dBm for per-chain power.

Test signals: interface start/stop, monitor mode packet visibility, SAR and txpower changes while idle/running, channel switch failures, survey updates, AP beacon continuity, and mac80211 callback coverage for station/key/AMPDU paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_mcu.c

Purpose: MT76x2U USB firmware loader and MCU radio initialization. It loads optional ROM patch, downloads ILM/DLM firmware over USB/FCE, starts the MCU, and enables radio functions.

Important APIs: `mt76x2u_mcu_fw_init` and `mt76x2u_mcu_init`. Internal helpers send vendor/class commands for IVB loading, patch enable, WMT reset, ROM patch loading, and firmware loading.

Control flow: ROM patch loading optionally acquires a hardware semaphore, checks whether the patch is already active, requests firmware, validates header, configures USB DMA and FCE, resets MCU, sends patch chunks to `MT76U_MCU_ROM_PATCH_OFFSET`, enables patch, resets WMT, polls patch status, releases semaphore, and releases firmware. Main firmware loading validates ILM/DLM lengths, logs version/build, resets MCU, configures DMA/FCE, sends ILM and DLM chunks, loads IVB, polls firmware start bit, sets running bit, and records ethtool firmware version. MCU init selects queue function and turns radio on.

State and persistence: firmware files are module firmware dependencies; runtime state includes MCU registers, hardware semaphore, firmware version, USB transfer buffers, and radio state.

Dependencies and integration: depends on Linux firmware loader, mt76 USB vendor requests, mt76x02 firmware header structures, FCE register programming, and common MCU function/radio commands.

Risks: malformed firmware lengths or failed chunk transfers must not leave semaphores held. Revision-specific patch bits and DLM offsets are fragile. The shared `usb->data` buffer is used for control payloads and assumes serialized MCU setup.

Test signals: missing/invalid firmware files, ROM patch already-applied path, semaphore timeout, E3 versus older revision offsets, successful ethtool firmware version, and recovery after firmware start timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_phy.c

Purpose: USB-specific channel programming and periodic PHY calibration for MT76x2U, layered on shared MT76x2 PHY helpers.

Important APIs: `mt76x2u_phy_set_channel` and delayed-work callback `mt76x2u_phy_calibrate`. Internal `mt76x2u_phy_channel_calibrate` runs once per channel unless the channel is silent.

Control flow: channel set resets calibration state, derives hardware channel, bandwidth, bandwidth index, and extension CCA mapping from chandef, reads RX gain, configures txpower registers, tx delay, txpower, band, bandwidth, CCA fields, and MCU channel. It then initializes gain, enables LDPC on newer revisions, performs R/RC/RXDCOC and channel calibrations when appropriate, sets AGC/TXOP/RXO registers, initializes TSSI default compensation, optionally runs TSSI calibration, queues periodic calibration, and returns. The periodic worker locks the device, completes channel calibration if needed, runs TSSI compensation and gain update, then reschedules itself.

State and persistence: runtime calibration state includes `channel_cal_done`, `init_cal_done`, `tssi_cal_done`, `cal_work`, scan state, current chandef, and AGC gain values.

Dependencies and integration: depends on shared `phy.c`, `usb_mac.c` stop/resume, mt76x02 MCU calibration commands, EEPROM flags, EDCCA, AGC helpers, and mac80211 workqueue scheduling.

Risks: channel/bandwidth index math is central to regulatory and RF correctness. Calibration is skipped during scanning/silent channels, so stale calibration state can matter. Worker rescheduling must be cancelled during stop/cleanup to avoid register access after removal.

Test signals: 20/40/80 MHz channel switches, upper/lower 40 MHz extension mapping, scanning path, TSSI-enabled and disabled EEPROMs, silent-channel behavior, calibration work cancellation, and LDPC enable on E3+ revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/Kconfig

Purpose: Build-time configuration for MT7915-family drivers. It exposes PCIe MT7915E support and optional MT798x SoC WMAC support.

Important symbols: `MT7915E` is tristate, depends on `MAC80211` and `PCI`, selects `MT76_CONNAC_LIB`, `WANT_DEV_COREDUMP`, and `RELAY`. `MT798X_WMAC` is bool, depends on `MT7915E` and `ARCH_MEDIATEK || COMPILE_TEST`, and selects `REGMAP`.

Control flow: there is no runtime control flow; Kconfig controls which objects can be built and which supporting kernel subsystems are pulled in.

State and persistence: persistent state is kernel configuration. Enabling `MT7915E=m` builds a module; enabling `MT798X_WMAC` compiles SoC support into that driver build.

Dependencies and integration: ties the driver to mac80211, PCI, relay-based firmware logging, devcoredump request support, Connac common library, MediaTek SoC architecture support, and regmap for SoC access.

Risks: selecting `WANT_DEV_COREDUMP` is not the same as enabling `CONFIG_DEV_COREDUMP`; coredump code remains conditional in the Makefile/header. `MT798X_WMAC` cannot be selected independently of PCIe support, which may surprise SoC-only configurations.

Test signals: `allyesconfig`, `allmodconfig`, `COMPILE_TEST` on non-MediaTek arches, builds with and without `CONFIG_DEV_COREDUMP`, and module dependency inspection for relay/mac80211/mt76_connac.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/Makefile

Purpose: Object composition for the `mt7915e` driver module.

Important entries: `obj-$(CONFIG_MT7915E) += mt7915e.o`; base objects are `pci.o init.o dma.o eeprom.o main.o mcu.o mac.o debugfs.o mmio.o`; optional objects include `testmode.o` for `CONFIG_NL80211_TESTMODE`, `soc.o` for `CONFIG_MT798X_WMAC`, and `coredump.o` for `CONFIG_DEV_COREDUMP`.

Control flow: no runtime flow; the Makefile determines which translation units are linked into the driver.

State and persistence: persistent state is kernel configuration and module build output. Optional object inclusion changes available runtime features such as testmode, SoC support, and firmware coredump.

Dependencies and integration: mirrors declarations in Kconfig and header stubs. `coredump.h` provides no-op inline functions when `coredump.o` is absent, allowing callers in `init.c`/`mac.c` to compile.

Risks: adding calls to functions from optional objects requires matching stubs or Makefile updates. Missing `coredump.o` with `CONFIG_DEV_COREDUMP` would break firmware crash reporting; adding new source files without updating this list silently omits functionality.

Test signals: build matrix with `CONFIG_MT7915E=n/m/y`, `CONFIG_NL80211_TESTMODE`, `CONFIG_MT798X_WMAC`, and `CONFIG_DEV_COREDUMP`; inspect `nm`/modinfo to confirm expected optional symbols and firmware declarations elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/coredump.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/coredump.c

Purpose: Firmware crash dump assembly for MT7915/MT7916/MT798x devices, with optional firmware memory dumping exposed through Linux devcoredump.

Important APIs: `mt7915_coredump_get_mem_layout`, `mt7915_coredump_new`, `mt7915_coredump_submit`, `mt7915_coredump_register`, and `mt7915_coredump_unregister`. Internal helpers compute memory size and collect firmware state, trace, stack, task, and context information.

Control flow: registration allocates `dev->coredump.crash_data` and optionally a memory buffer based on chip-specific region layout when `coredump_memdump=1`. On crash, `mt7915_coredump_new` records GUID/timestamp under `dump_mutex`; `mt7915_coredump_build` allocates a packed dump, copies metadata, reads firmware exception registers, traces, task queues, context, call stack, and optional pre-collected memory, then `dev_coredumpv` submits it.

State and persistence: crash data persists in `dev->coredump.crash_data` across crashes until unregister. The module parameter `coredump_memdump` controls large memory capture. Dump payload contains kernel/fw version, chip id, exception state, traces, and optional memory region data.

Dependencies and integration: called by init/register/unregister and `mt7915_mac_dump_work`; uses devcoredump, `vzalloc`, UTS name, GUID/time helpers, register access, and `mt7915_memcpy_fromio`.

Risks: memory layout lengths are hardware-specific and large; buffer length accounting must stay aligned with headers. `mt7915_coredump_unregister` assumes `crash_data` exists. Trace loops copy large fixed arrays and rely on firmware register formats varying by chip.

Test signals: firmware assert via debugfs, coredump with and without memdump, chip variants 7915/7916/7981/7986, devcoredump userspace retrieval, unregister after failed partial registration, and lockdep around `dump_mutex`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/coredump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/coredump.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/coredump.h

Purpose: Data contract and conditional API declarations for MT7915 firmware coredumps.

Important types: `struct trace`, `struct mt7915_coredump`, `struct mt7915_coredump_mem`, `struct mt7915_mem_hdr`, and `struct mt7915_mem_region`. Public functions are declared when `CONFIG_DEV_COREDUMP` is enabled; otherwise inline stubs return benign defaults.

Control flow: no runtime flow in the header. It defines the packed binary format consumed by `coredump.c` and allows `init.c`/`mac.c` to call coredump APIs unconditionally.

State and persistence: the packed dump format persists in devcoredump output. It includes magic, length, GUID, wall-clock time, kernel and firmware versions, device id, firmware state, trace indices, sched/irq traces, task queue/stack info, context, call stack, and flexible memory data.

Dependencies and integration: includes `mt7915.h`, uses `guid_t`, ethtool firmware version length, and chip-specific crash data from the main device structure.

Risks: packed layout is an ABI for debugging tools; field reordering or size changes can break parsers. Flexible arrays require careful allocation math. Stub behavior means callers cannot infer coredump availability from successful register/submit return alone when the feature is compiled out.

Test signals: compile with and without `CONFIG_DEV_COREDUMP`, static layout/size expectations for parsers, successful no-op behavior with stubs, and dump parser validation against real crash artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/coredump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/debugfs.c

Purpose: Debugfs, relay logging, diagnostics, and test controls for MT7915 PHYs and stations.

Important APIs: `mt7915_init_debugfs`, `mt7915_debugfs_rx_fw_monitor`, `mt7915_debugfs_rx_log`, and `mt7915_sta_add_debugfs`. File operations cover implicit TXBF, system error recovery, radar trigger, MURU stats/debug, firmware WM/WA/bin logging, firmware CPU utilization, hardware queues, TX stats, txpower SKU/path, TWT stats, RF register access, and per-station fixed rate/queues.

Control flow: init registers per-phy debugfs files, saving the main phy directory for relay logging. Firmware debug setters program MCU log routing and open/reset a relay channel for binary logs. SER debugfs writes can query recovery, enable and trigger L1/L2/L3 recovery, request full reset, or intentionally assert firmware. Read paths format register/MIB state through seq_file or simple buffers. Per-station debugfs can translate user rate tuples into MCU fixed-rate controls.

State and persistence: runtime knobs mutate `dev->ibf`, `dev->muru_debug`, `dev->fw.debug_*`, relay channel state, txpower tables, recovery counters, and per-station fixed-rate state. Most data is volatile hardware/firmware state exposed for diagnostics.

Dependencies and integration: depends on debugfs, relayfs, mac80211 debugfs, mt7915 MCU commands, MAC stats, EEPROM SKU lengths, DFS/RDD helpers, and register access.

Risks: debugfs write knobs are privileged but powerful: firmware crash, full reset, RF writes, txpower override, and fixed rates can disrupt operation or regulatory behavior. Formatting code must avoid buffer overflow; relay logging needs synchronization, handled by a static spinlock. Many reads assume hardware is responsive.

Test signals: debugfs file creation for main/ext PHY, enable/disable firmware logs, relay data capture, SER trigger paths, txpower read/write validation, MURU stats after enabling, radar trigger error paths, fixed-rate input parsing, and cleanup on device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/dma.c

Purpose: DMA ring configuration, queue allocation, interrupt enablement, WED integration, and reset/cleanup for MT7915-family devices.

Important APIs: `mt7915_dma_prefetch`, `mt7915_dma_start`, `mt7915_dma_init`, `mt7915_dma_reset`, and `mt7915_dma_cleanup`. Internal helpers configure queue IDs/interrupt masks, initialize TX queues, poll TX completion NAPI, disable/enable DMA, and set prefetch windows.

Control flow: `mt7915_dma_config` maps logical RX/TX/MCU queues to chip-specific WFDMA engines, interrupts, and hardware ring ids. Init attaches DMA, disables/reset WFDMA, configures WED if active, allocates main/ext phy TX rings, MCU WM/WA/FWDL rings, MCU event RX rings, data RX rings, txfree RX rings, initializes NAPI/queues, and enables DMA. Start enables global WFDMA bits, computes interrupt masks by band/DBDC/WED state, optionally starts WED and RX stats, then enables interrupts. Reset drains TX/RX/MCU queues, optionally resets WFSYS, resets WED/DMA queues/tokens, restarts RX queues, and re-enables DMA.

State and persistence: mutable state includes `wfdma_mask`, `q_int_mask`, `q_id`, queue descriptors, rx token size, WED queue flags/pointers, NAPI state, and interrupt masks.

Dependencies and integration: depends on mt76 DMA core, mt76_connac queue helpers, MediaTek WED offload APIs, chip predicates, register definitions, and reset code in `init.c`/`mac.c`.

Risks: chip-specific queue mappings are dense and easy to break. WED paths alter ring bases, queue IDs, token sizing, and interrupts. Reset must avoid resetting WED txfree queues incorrectly and must preserve NAPI ordering.

Test signals: boot and traffic on MT7915, MT7916, MT7981/7986, DBDC with hif2, WED on/off and RX-capable WED, DMA reset during traffic, txfree accounting, interrupt storm/idle behavior, and NAPI cleanup on unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/eeprom.c

Purpose: EEPROM/efuse/default-bin loading and capability/power parsing for MT7915-family devices.

Important APIs: `mt7915_eeprom_init`, `mt7915_eeprom_parse_hw_cap`, `mt7915_eeprom_get_target_power`, `mt7915_eeprom_get_power_delta`, `mt7915_eeprom_has_background_radar`, and `mt7915_sku_group_len`.

Control flow: initialization attempts `mt76_eeprom_init`; flash mode is accepted directly, otherwise the driver checks efuse free blocks and reads EEPROM blocks through MCU. Invalid/missing EEPROM falls back to chip/adie/dbdc-specific default firmware bin. Precal data is optionally loaded from MTD or nvmem if EEPROM flags request it. Hardware capability parsing sets band support, 5/6 GHz choice, chainmask, antenna mask, DBDC chain shifts, and MAC address. Power helpers compute per-channel target power and rate delta by band/chip/adie/TSSI state.

State and persistence: EEPROM bytes live in `mt76.eeprom.data`; `dev->flash_mode`, `dev->cal`, `chainmask`, `chainshift`, band capabilities, and MAC address are derived state. `enable_6ghz` module parameter can force 6 GHz instead of 5 GHz for dual-capable hardware and mutates the buffered EEPROM band field.

Dependencies and integration: depends on Linux firmware loader, mt76 EEPROM/MTD/nvmem helpers, mt7915 MCU EEPROM access, `eeprom.h` offsets, chip/adie predicates, and txpower initialization in `init.c`.

Risks: bad EEPROM fallback can mask board data problems. Free-block heuristic for efuse sufficiency is hardware-specific. 6 GHz selection forces flash/buffer mode and can affect regulatory exposure. Power offsets differ by chip generation and TSSI state.

Test signals: flash EEPROM, efuse-only, invalid EEPROM fallback, default bins for 7915/7916/7981/7986/adie variants, precal MTD/nvmem presence and absence, DBDC chain masks, 6 GHz module parameter, and per-band txpower results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/eeprom.h

Purpose: EEPROM offset map, calibration sizes, band/SKU enums, and inline helpers for MT7915-family EEPROM interpretation.

Important definitions: `enum mt7915_eeprom_field`, calibration flags and sizes, Wi-Fi configuration bit masks, rate delta masks, `enum mt7915_adie_sku`, band selection enums, `enum mt7915_sku_rate_group`, `mt7915_get_channel_group_5g`, `mt7915_get_channel_group_6g`, `mt7915_tssi_enabled`, `mt7915_get_cal_group_size`, and `mt7915_get_cal_dpd_size`.

Control flow: inline helpers map channel numbers to EEPROM power groups, inspect EEPROM config bits for TSSI enablement, and select group/DPD precal sizes by chip, band, and adie generation.

State and persistence: this header documents the persistent EEPROM layout. Callers read `dev->mt76.eeprom.data` and chip/adie state to derive calibration sizes, target-power indices, band capabilities, and TSSI behavior.

Dependencies and integration: included by EEPROM, init, debugfs, and power code. Depends on `mt7915.h`, Linux bitfield helpers, and chip/adie helper functions provided elsewhere.

Risks: offsets are hardware ABI. A wrong offset or group-size constant can make EEPROM reads corrupt capability/power interpretation or allocate the wrong precal buffer size. 6 GHz fields only appear in v2 layout, so callers must guard old hardware.

Test signals: unit-style validation of channel group mapping boundaries, EEPROM fixture parsing for all supported chips/adies, TSSI bit behavior for DBDC and non-DBDC, precal size selection, and build coverage for all includers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/init.c

Purpose: Main registration and hardware initialization spine for MT7915-family devices. It defines mac80211 capabilities, thermal/hwmon/LED support, txpower initialization, MAC defaults, DBDC/ext-phy registration, WFSYS reset, and device unregister.

Important APIs: `mt7915_init_txpower`, `mt7915_mac_init`, `mt7915_txbf_init`, `mt7915_wfsys_reset`, `mt7915_set_stream_vht_txbf_caps`, `mt7915_set_stream_he_caps`, `mt7915_register_device`, and `mt7915_unregister_device`.

Control flow: register initializes work items/lists/waitqueues/mutexes, determines band/DBDC config, allocates ext phy, initializes DMA/MCU/EEPROM/global WCID, configures wiphy capabilities, registers the main mt76 device, initializes thermal support, registers ext phy if present, queues deferred EEPROM/MAC/TXBF init, enables debugfs and coredump. Hardware init masks interrupts, starts DMA, MCU, EEPROM, optional group calibration, and allocates global WCID. Unregister cancels work, unregisters ext phy/coredump/thermal/mac80211, stops hardware, and frees device.

State and persistence: initializes `dev->phy`, `dbdc_support`, ext phy band index, lists for station rate-control and TWT, reset/coredump work, thermal thresholds/state, MAC/LED registers, chain and txpower state, and recovery readiness.

Dependencies and integration: depends on mac80211, mt76 core registration, DMA/MCU/EEPROM/MAC/debugfs/coredump modules, thermal and hwmon subsystems, LED support, device-tree radar property, and WED capability.

Risks: registration unwind is complex and must mirror initialization order. Ext phy MAC fallback must avoid address collisions. HE/VHT capability generation depends on chip/DBDC stream limits. Thermal threshold validation uses inverted critical/max naming conventions from hardware.

Test signals: build/register/unregister for each chip family, DBDC and single-band modes, ext-phy failure unwind, thermal sysfs and cooling device, LED blink/brightness, HE/VHT capability advertisement, coredump registration failures, and WFSYS reset recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mac.c

Purpose: Core MAC datapath, statistics, reset recovery, DFS radar, and TWT scheduling for MT7915-family devices.

Important APIs: `mt7915_mac_wtbl_update`, `mt7915_mac_wtbl_lmac_addr`, `mt7915_mac_write_txwi`, `mt7915_tx_prepare_skb`, `mt7915_wed_init_buf`, `mt7915_rx_check`, `mt7915_queue_rx_skb`, `mt7915_mac_cca_stats_reset`, `mt7915_mac_reset_counters`, `mt7915_mac_set_timing`, `mt7915_mac_enable_nf`, `mt7915_update_channel`, `mt7915_mac_reset_work`, `mt7915_mac_dump_work`, `mt7915_reset`, `mt7915_mac_update_stats`, `mt7915_mac_sta_rc_work`, `mt7915_mac_work`, `mt7915_dfs_init_radar_detector`, `mt7915_mac_add_twt_setup`, and `mt7915_mac_twt_teardown_flow`.

Control flow: RX dispatch separates txfree notifications, MCU events, RX vectors, TX status, firmware monitor logs, and normal frames. Normal RX parses RX descriptors, security flags, WCID, checksum, radiotap/rate vectors, A-MSDU state, header translation, PPE/WED metadata, and sequence/QoS fields before passing frames to mt76. TX preparation allocates tokens, writes connac TXWI, attaches firmware TXP buffers, and requests periodic TX status. Reset work handles full firmware crash recovery with coredump and restart, or partial DMA-stop recovery synchronized with MCU state bits. Periodic MAC work updates survey/stats, severe checks, MURU stats, and TX status. DFS configures region-specific radar patterns and RDD state. TWT validates and schedules individual agreements, then mirrors them to firmware.

State and persistence: maintains WCID airtime, ack RSSI EWMA, token IDR, MIB accumulators, noise filter, reset/recovery flags, coredump crash data, DFS state, TWT table/list masks, and station rate-control work lists.

Dependencies and integration: depends on mt76_connac2 TX/RX helpers, DMA/WED, MCU command layer, debugfs firmware log sink, coredump, mac80211 station/TWT/DFS APIs, and register definitions.

Risks: descriptor parsing is length-sensitive and must reject malformed SKBs before pointer overrun. Token release and WED offload accounting are concurrency-sensitive. Reset sequencing spans NAPI, workers, MCU waitqueues, DMA, and mac80211 queues. DFS radar constants are regulatory critical. TWT list scheduling must avoid overlapping agreements and stale table masks.

Test signals: RX with encrypted/plain/header-translated/A-MSDU frames, malformed descriptor fuzzing, TX token exhaustion/release, WED on/off, firmware monitor logs, full and partial SER recovery, MIB counter growth, DFS CAC/active/stop transitions per region, TWT accept/reject/teardown, and long-running watchdog behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mac.h

Purpose: MAC descriptor bit definitions and DFS radar specification structures shared by MT7915 MAC code.

Important definitions: TX-free descriptor masks for old/new formats, TX status fields for MPDU counts/noise/RCPI/retry/fail bytes, and `struct mt7915_dfs_pulse`, `struct mt7915_dfs_pattern`, `struct mt7915_dfs_radar_spec`.

Control flow: no executable flow. `mac.c` consumes the TX-free masks while parsing firmware notifications and uses DFS structures to build region-specific radar tables passed to MCU commands.

State and persistence: the header defines descriptor ABI state exchanged with firmware/hardware and packed DFS radar pattern data. The DFS structures encode regulatory detection parameters such as pulse width, power, PRI ranges, and staggered radar properties.

Dependencies and integration: includes `mt76_connac2_mac.h`; used by `mac.c`, `debugfs.c`, and init paths that need MAC/DFS declarations.

Risks: bit masks must match firmware descriptor versions exactly. Confusing V0/V3 TX-free fields can corrupt token release or retry accounting. DFS structures are packed, so field ordering and width are part of the MCU command payload contract.

Test signals: compile-time use across `mac.c`/`debugfs.c`, txfree parsing on descriptor versions 0 and 4, retry/failure stat accuracy, DFS radar setup command payload inspection, and sparse/endian checks for packed structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mac.h -->
