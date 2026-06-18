# subset-b-004851 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mt7603.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mt7603.h

Purpose: private MT7603/MT7628 driver header defining the chip constants, core private state, per-VIF/per-STA state, reset reasons, firmware names, ring sizes, and internal APIs shared by the mt7603 implementation files.

Important APIs/types/functions: declares `struct mt7603_dev`, `struct mt7603_sta`, `struct mt7603_vif`, `struct mt7603_rate_set`, `enum mt7603_reset_cause`, `enum mt7603_bw`, `is_mt7603()`, `is_mt7628()`, IRQ mask helpers, and prototypes for registration, EEPROM, DMA, MCU, MAC, WTBL, TX/RX, station, EDCCA, and debugfs operations. `struct mt7603_dev` embeds `mt76_dev`/`mt76_phy` first so generic mt76 container logic can treat it as either base type.

Control flow: this header does not execute control flow directly, but it fixes the lifecycle contract used by bus glue and common code: allocate `mt7603_dev`, initialize MMIO/bus ops, load EEPROM and firmware, initialize DMA/MAC/WTBL, register mac80211 operations, then service IRQ, TX/RX, station events, watchdog/reset, and EDCCA work through the declared functions.

State and persistence: persistent in-memory state includes RX filter bits, AGC/CCA statistics, rate retry state per station, power-save queues, ED monitor thresholds, dynamic sensitivity, watchdog counters, DMA index snapshots, reset test controls, and reset cause counters. Nonvolatile inputs are firmware blobs and EEPROM/OTP calibration data read elsewhere.

Dependencies and integration: depends on Linux interrupt/time/skbuff/mac80211 types, mt76 core abstractions from `../mt76.h`, and register definitions from `regs.h`. It is the integration point between `pci.c`/`soc.c` bus drivers and the rest of the MT7603 driver.

Risks: layout comments such as "must be first" are ABI-sensitive with container casts; changing them can corrupt generic mt76 access. WTBL index constants reserve top entries for VIF/global use and must stay aligned with hardware table size. Watchdog/reset and EDCCA fields are shared across interrupt, workqueue, and mac80211 paths and require locking discipline in implementation files.

Test signals: build coverage of all mt7603 objects catches prototype/register drift. Runtime signals include successful probe firmware selection (`mt7603_e*.bin` or `mt7628_e*.bin`), interface add/remove, station association, TX/RX traffic, EDCCA tuning, and reset-cause counters exposed by debugfs or logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/mt7603.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/pci.c

Purpose: PCI bus glue for MT7603 devices. It binds MediaTek PCI device ID `0x7603`, maps BAR0, sets DMA capability, wires the shared IRQ handler, and hands the allocated device to common MT7603 registration.

Important APIs/functions: defines `mt76pci_device_table`, `mt76pci_probe()`, `mt76pci_remove()`, and exported `struct pci_driver mt7603_pci_driver`. Uses `pcim_enable_device`, `pcim_iomap_regions`, `pci_set_master`, `dma_set_mask`, `mt76_alloc_device`, `mt76_mmio_init`, `devm_request_irq`, `mt7603_register_device`, and `mt7603_unregister_device`.

Control flow: probe enables the PCI function, maps BAR0, enables bus mastering, restricts DMA to 32 bits, allocates an mt76-backed `mt7603_dev`, initializes MMIO, reads chip ID/revision registers, masks interrupts, requests a shared IRQ, then calls common registration. Any failure after allocation frees the mt76 device. Remove fetches driver data from PCI state and unregisters the common device.

State and persistence: initializes only runtime state: MMIO base, ASIC revision in `mdev->rev`, IRQ registration, and mt76/mac80211 registration side effects. Firmware names are declared with `MODULE_FIRMWARE` but loading happens in common MCU code.

Dependencies and integration: depends on Linux PCI/module/DMA APIs and the common declarations in `mt7603.h`. `mt7603_register_device()` is responsible for setting PCI drvdata, mac80211 registration, firmware, DMA, and hardware setup.

Risks: only 32-bit DMA is accepted; systems requiring a different mask will fail probe. Interrupts are masked before request, but ordering with common registration must keep the device quiet until handlers and rings are ready. Error handling frees the mt76 allocation but relies on devm/pcim for IRQ and mapping cleanup.

Test signals: PCI modalias/module autoload for vendor MediaTek device `0x7603`, successful "ASIC revision" log, IRQ request success, firmware request for `mt7603_e1.bin`/`mt7603_e2.bin`, and clean unload/reprobe without leaked IRQs or stale netdevs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/regs.h

Purpose: MT7603 register map and bitfield catalog. It assigns offsets and masks for top-level revision/chip ID, MCU remap, HIF/WPDMA rings, PSE flow control, PHY/AGC/RXTD, aggregation, DMA filters, WMM arbitration, TMAC/RMAC, security, WTBL, LPON timers, hardware interrupts, MIB counters, LED registers, client/PSE physical windows, and efuse access.

Important APIs/macros: defines register base helpers such as `MT_MCU()`, `MT_HIF()`, `MT_PSE()`, `MT_WF_PHY()`, `MT_WF_AGG()`, `MT_WF_DMA()`, `MT_WF_ARB()`, `MT_WF_TMAC()`, `MT_WF_RMAC()`, `MT_WF_SEC()`, `MT_WTBL_OFF()`, `MT_LPON()`, and bitfields consumed through `FIELD_PREP`, `FIELD_GET`, `mt76_rr`, `mt76_wr`, and `mt76_rmw`. WTBL layout macros describe multiple WTBL banks and per-word fields for address, key, QoS, HT/VHT, BA, rate, sequence, and counters.

Control flow: no executable flow, but the map drives all register programming in the MT7603 driver. Implementations use it for interrupt masking, DMA start/reset, scheduler and queue programming, filter programming, beacon timers, WTBL updates, EEPROM/efuse reads, LED control, CCA/MIB reads, and reset/watchdog diagnostics.

State and persistence: represents volatile hardware state. Persistent information enters through efuse/EEPROM registers; runtime state lives in hardware tables, DMA ring registers, MIB counters, and WTBL entries. Several counters are read-clear or require explicit clear bits, so call ordering matters.

Dependencies and integration: included by `mt7603.h` and all mt7603 implementation files. It relies on Linux bit macros (`BIT`, `GENMASK`) and mt76 MMIO helpers. Physical remap constants connect high physical blocks such as LED/client/PSE/efuse into PCIe remap windows.

Risks: a typo in a bit mask or offset can silently corrupt unrelated hardware state; two entries use `GENAMSK` spelling (`MT_WTBL2_W5_FAIL_COUNT_RATE1`, `MT_WTBL2_W13_AVG_RCPI2`) and will fail if referenced. Remap base/offset masks must match silicon windows. WTBL bank sizing depends on `MT7603_WTBL_SIZE`, so changing table size without recalculating offsets is unsafe.

Test signals: compile-time reference coverage catches macro spelling only when used. Runtime validation comes from working interrupt delivery, DMA rings, beacon timing, association/security setup, LED control, efuse reads, and sane MIB/WTBL debug values under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/soc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/soc.c

Purpose: platform/SoC bus glue for the MT7628 integrated WMAC variant of the MT7603 driver.

Important APIs/functions: defines `mt76_wmac_probe()`, `mt76_wmac_remove()`, OF match table for `"mediatek,mt7628-wmac"`, and exported `struct platform_driver mt76_wmac_driver`. Uses `platform_get_irq`, `devm_platform_ioremap_resource`, `mt76_alloc_device`, `mt76_mmio_init`, `devm_request_irq`, `mt7603_register_device`, and `mt7603_unregister_device`.

Control flow: probe retrieves the platform IRQ and MMIO resource, allocates an mt76-backed `mt7603_dev`, initializes MMIO, reads chip ID/revision, masks interrupts, registers the shared IRQ handler, then calls common device registration. Failures after allocation free the mt76 device. Remove obtains driver data from platform state and unregisters the common device.

State and persistence: initializes only runtime state: mapped SoC MMIO, IRQ registration, ASIC revision, and common driver registration state. Firmware blobs `mt7628_e1.bin` and `mt7628_e2.bin` are advertised for later MCU loading.

Dependencies and integration: depends on Linux platform device and OF matching. Shares almost all common code with the PCI variant through `mt7603.h`, making the bus layer intentionally thin.

Risks: probe assumes a single IRQ and a single MMIO resource in device tree. If common registration does not set platform drvdata, remove cannot locate `mt76_dev`. IRQ is requested as shared; interrupt masking before common init is important to avoid early spurious handling.

Test signals: device-tree match on `mediatek,mt7628-wmac`, successful ASIC revision log, firmware load for MT7628 blobs, interface bring-up on SoC targets, and clean driver unbind/rebind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/soc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/Kconfig

Purpose: kernel configuration menu for MT7615/MT7622/MT7663 driver variants and their common support objects.

Important symbols: `MT7615_COMMON` selects `WANT_DEV_COREDUMP` and `MT76_CONNAC_LIB`; `MT7615E` enables PCIe MT7615/MT7663 support and depends on MAC80211 and PCI; `MT7622_WMAC` enables integrated MT7622 WMAC support when `MT7615E` and MediaTek architecture or compile-test are available and selects REGMAP; `MT7663_USB_SDIO_COMMON` feeds shared USB/SDIO code; `MT7663U` selects `MT76_USB`; `MT7663S` selects `MT76_SDIO`.

Control flow: Kconfig selections determine which objects the Makefile builds. Enabling any transport selects the common mt7615 implementation; transport-specific symbols add PCI, SoC, USB, or SDIO entry points and bus libraries.

State and persistence: no runtime state. Build-time choices affect module availability, firmware declarations compiled into modules, and whether coredump/regmap/USB/SDIO dependencies are present.

Dependencies and integration: integrates the driver with kernel `drivers/net/wireless/mediatek/mt76` build configuration. The help text documents hardware capabilities and module build expectations for users.

Risks: `MT7622_WMAC` depends on `MT7615E`, so SoC support is tied to the PCIe driver symbol and common PCIe object grouping. Missing `MAC80211`, `PCI`, `USB`, or `MMC` dependencies prevent the expected transport from building. `default y` for MT7622 under its dependencies can increase build coverage and binary surface.

Test signals: `make menuconfig` visibility, randconfig/allmodconfig coverage, correct module object generation for each selected transport, and modinfo showing expected firmware and aliases from corresponding source files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/Makefile

Purpose: object composition for MT7615/MT7663 kernel modules.

Important targets: builds `mt7615-common.o`, `mt7615e.o`, `mt7663-usb-sdio-common.o`, `mt7663u.o`, and `mt7663s.o` according to Kconfig symbols. `mt7615-common-y` includes `main.o`, `init.o`, `mcu.o`, `eeprom.o`, `mac.o`, `debugfs.o`, and `trace.o`, with optional `testmode.o`. `mt7615e-y` includes PCI/MMIO/DMA pieces and optional `soc.o` for MT7622.

Control flow: kbuild links common code into all relevant transports, then adds transport-specific bus and DMA implementations. Trace compilation gets `CFLAGS_trace.o := -I$(src)` so generated trace headers can include local paths.

State and persistence: no runtime state. Build composition determines which source files share a module namespace and which symbols must be exported for cross-object use.

Dependencies and integration: driven by `Kconfig` symbols and kbuild conventions. Connects common mac80211/MCU/MAC/EEPROM/debug code with PCI, SoC, USB, and SDIO transport files in the same driver family.

Risks: missing an object here can produce unresolved symbols or silently omit transport behavior. Common code exports are necessary because some functions are shared across modules/transports. Optional testmode compilation must stay consistent with declarations guarded by `CONFIG_NL80211_TESTMODE`.

Test signals: successful `M=drivers/net/wireless/mediatek/mt76/mt7615` builds across PCI, SoC, USB, SDIO, and testmode configs; generated module contents match selected Kconfig symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/debugfs.c

Purpose: debugfs interface for MT7615/MT7663 runtime inspection and low-level control.

Important APIs/functions: provides debugfs attributes for register read/write (`regval` via mt76 core), radar pattern trigger, chip config, SCS, runtime PM, idle timeout, DBDC toggling, firmware debug logs, reset-test injection, AMPDU stats, radio sensitivity/false CCA, AC queue depth, TX queue status, RF register access, extra MAC address table manipulation, and SDIO scheduler quota. Entry point is `mt7615_init_debugfs()`.

Control flow: most setters first check MCU readiness with `mt7615_wait_for_mcu_init()`, then acquire the driver mutex before sending MCU commands or touching hardware. Runtime PM toggling refuses unsupported firmware/bus combinations and AP beacon activity, wakes the chip, flips `pm->enable`, and reschedules power-save work. DBDC debugfs dynamically registers/unregisters the second PHY. `reset_test` injects a tiny raw skb to exercise reset paths. Read handlers snapshot hardware queues, MIB-derived AMPDU stats, RF registers, or MUAR entries.

State and persistence: writes alter live driver and hardware state: `dev->fw_debug`, `dev->pm.enable`, `dev->pm.idle_timeout`, `dev->muar_mask`, radar test pattern fields, RF register selector fields, and possibly second-PHY registration. Changes are not persistent across driver reload unless firmware or external config preserves them.

Dependencies and integration: uses Linux debugfs/seq_file helpers, mt76 debugfs registration, MCU helpers, MAC SCS controls, RF accessors, PM state, and SDIO scheduler structures. Debugfs files are installed under the mt76 PHY debugfs directory.

Risks: low-level register/RF writes can destabilize hardware. `ext_mac_addr` accepts user-provided entries and programs MUAR hardware directly. Runtime PM and DBDC toggles are constrained but still race-sensitive with running interfaces if external callers bypass expected mac80211 state. Some file operations are unsafe by design (`debugfs_create_file_unsafe`).

Test signals: presence of debugfs files after registration; `regval` read/write against benign registers; `runtime_pm_stats` showing awake/doze transitions; `xmit-queues` and `acq` changing under traffic; `fw_debug` enabling firmware log events; DBDC file registering a secondary PHY only while the device is stopped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/dma.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/dma.c

Purpose: DMA and queue initialization/cleanup for MT7615 PCIe/MMIO-style devices and related MT7622/MT7663 variants.

Important APIs/functions: defines TX queue setup (`mt7615_init_tx_queues()`, `mt7622_init_tx_queues_multi()`), NAPI pollers (`mt7615_poll_rx()`, `mt7615_poll_tx()`), busy polling (`mt7615_wait_pdma_busy()`), DMA scheduler setup for MT7622/MT7663, `mt7615_dma_start()`, `mt7615_dma_init()`, and `mt7615_dma_cleanup()`.

Control flow: `mt7615_dma_init()` attaches mt76 DMA, programs WPDMA global flags and MT7615-specific prefetch/abort settings, resets ring indices, initializes firmware-download and WM MCU queues, initializes data/mgmt queues according to chip type, allocates MCU and main RX rings, installs RX/TX NAPI handlers, waits for idle DMA, enables TX/RX/MCU interrupts, then starts DMA and scheduler quotas. Pollers take runtime-PM references; if the chip is asleep they complete NAPI and queue wake work. Cleanup disables DMA, asserts software reset, and delegates ring cleanup to mt76.

State and persistence: initializes volatile DMA ring state, queue descriptors, interrupt masks, NAPI state, WPDMA configuration, and DMASHDL quotas. No disk persistence; ring contents and hardware queue state reset across device removal/reset.

Dependencies and integration: depends on mt76 DMA core (`../dma.h`), mt76 queue allocation helpers, connac runtime PM, chip tests (`is_mt7615`, `is_mt7622`, `is_mt7663`), and register definitions. Feeds RX packets into `mac.c` through mt76 queue plumbing.

Risks: queue IDs and ring sizes differ by chip; wrong mapping can starve AC/MCU queues. Runtime-PM reference failures must wake the device without losing NAPI progress. Busy polling timeouts indicate stuck PDMA/PSE and should block reset/start sequences. DMA scheduler quota values are hard-coded hardware tuning.

Test signals: successful probe with allocated TX/RX rings, interrupts for RX done and MCU TX done, no PDMA busy timeout, sustained traffic on all AC queues, firmware download through FWDL queue, and clean unload without DMA warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/dma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/eeprom.c

Purpose: EEPROM/efuse loading and hardware capability parsing for MT7615, MT7622, and MT7663.

Important APIs/functions: implements efuse block reads (`mt7615_efuse_read()`), OTP snapshot initialization, `mt7615_eeprom_init()`, EEPROM chip validation, band/chain capability parsing, target-power index helpers, power-delta lookup, and optional OTP calibration merge (`mediatek,eeprom-merge-otp`). Exports `mt7615_eeprom_init()`.

Control flow: EEPROM init allocates the full calibration buffer through mt76, reads efuse/OTP when present, validates the chip ID in EEPROM, falls back to OTP contents if EEPROM is invalid, otherwise marks `flash_eeprom` and optionally merges calibration-free OTP fields. It then derives band support, DBDC support, chainmask/antenna mask, copies the base MAC address, and lets mt76 apply EEPROM overrides. Power-index helpers branch by chip, band, chain, TSSI/external PA state, and 5 GHz channel group.

State and persistence: fills `dev->mt76.eeprom.data`, optional `dev->mt76.otp.data`, `dev->flash_eeprom`, `dev->dbdc_support`, `dev->chainmask`, `mphy` band capability flags, antenna/chain masks, and MAC address. EEPROM/OTP are persistent hardware data; parsed fields become runtime driver state.

Dependencies and integration: uses Linux OF properties, mt76 EEPROM helpers, register efuse access, `eeprom.h` offsets, and mac80211 band/channel types. Later init, MCU, and txpower code consume parsed chainmask, band capabilities, calibration flags, and power offsets.

Risks: efuse reads operate in 16-byte blocks and treat all-ones/invalid blocks as zero data; bad calibration can reduce performance. The fallback path copies OTP only if EEPROM validation fails, otherwise merges only selected calibration fields when explicitly requested. Chainmask parsing differs for MT7663 versus MT7615/MT7622 and relies on strap/eeprom bits being sane.

Test signals: valid EEPROM chip IDs `0x7615`, `0x7622`, or `0x7663`; expected 2 GHz/5 GHz/DBDC capabilities in wiphy; correct MAC address; sane antenna masks; txpower limits per channel; successful RX DCOC/TX DPD calibration when flash calibration bits are set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/eeprom.h

Purpose: EEPROM layout definitions, calibration block sizing, band/channel grouping helpers, and external-PA detection for MT7615-family devices.

Important APIs/macros: defines DCOC/TXDPD calibration offsets and full EEPROM size; `enum mt7615_eeprom_field` for chip ID, MAC, NIC/WiFi config, calibration flags, target power, rate power, and per-chip maximum offsets; rate-power and NIC config bit masks; `enum mt7615_eeprom_band`; `enum mt7615_channel_group`; `mt7615_get_channel_group()`; and `mt7615_ext_pa_enabled()`.

Control flow: inline helpers map 5 GHz channels into Japan/UNII groups for target-power lookup and infer external PA/TSSI state from EEPROM NIC config bits. The rest of the file is declarative.

State and persistence: describes persistent EEPROM/OTP fields used by `eeprom.c`, `init.c`, and `mcu.c`. Calibration payloads beyond base EEPROM are appended in the allocated EEPROM buffer for DCOC and TX DPD replay.

Dependencies and integration: includes `mt7615.h` for device type and mt76 EEPROM storage. Channel grouping feeds target-power index selection; external-PA logic affects target chain count and power source selection.

Risks: offsets are chip-specific and close together; mistakes can read wrong power/calibration data. `mt7615_ext_pa_enabled()` interprets cleared TSSI bits as external PA enabled, so inverted logic must be preserved. Channel group boundaries determine regulatory power behavior on 5 GHz channels.

Test signals: power index helpers returning expected offsets for 2 GHz and 5 GHz channels; calibration buffer size sufficient for all DCOC/TXDPD entries; external-PA platforms selecting external PA target-power bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/init.c

Purpose: common MT7615-family device/PHY initialization, wiphy capability setup, MAC defaults, txpower initialization, LED callbacks, thermal hwmon, and DBDC second-PHY registration.

Important APIs/functions: exports `mt7615_thermal_init()`, `mt7615_wait_for_mcu_init()`, `mt7615_init_txpower()`, `mt7615_init_work()`, `mt7615_reg_map()`, LED blink/brightness callbacks, `mt7615_register_ext_phy()`, `mt7615_unregister_ext_phy()`, and `mt7615_init_device()`. Internal helpers initialize PHY/MAC chains, offload capability, regulatory notifier, wiphy features, and DBDC antenna capabilities.

Control flow: `mt7615_init_device()` wires private PHY pointers, tx worker, PM work, MAC/scan/ROC/coredump work, waitqueues, timers, wiphy defaults, PM timeout, and testmode hooks. `mt7615_init_work()` sends EEPROM to firmware, programs MAC/PHY defaults, clears WTBL, and prunes unsupported offload ops. Starting from regulatory changes or channel changes, txpower is recalculated and sent to firmware when offload is active. DBDC registration can split antenna chains, allocate/register a second mt76 PHY, share queues, install scan/ROC work, and assign a locally administered MAC address.

State and persistence: initializes runtime state for `dev->phy`, `dev->pm`, workqueues, coredump queues, wiphy feature flags, antenna masks, txpower limits, LED registers, and optional second PHY. Thermal reads query firmware and expose millidegree Celsius via hwmon.

Dependencies and integration: ties mac80211 wiphy capabilities to mt76 helpers, MCU commands, EEPROM data, regulatory notifications, LED/hwmon subsystems, and register remapping. `mt7615_reg_map()` programs the PCIe remap register before accessing high physical addresses.

Risks: DBDC registration is refused while running; changing that would require careful queue and interface migration. Offload capability pruning mutates `dev->ops`, so function availability depends on firmware version. Regmap/remap accesses must be serialized. Thermal reads return zero if MCU init has not completed.

Test signals: wiphy reports correct interface combinations, bands, antenna masks, scan limits, and offload features; hwmon `temp1_input` works; regulatory changes update txpower and DFS setup; DBDC debugfs toggling creates/removes a second phy before start; LED callbacks program visible blink/brightness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mac.c

Purpose: descriptor-level MAC logic for MT7615-family devices: RX parsing, TX descriptor generation, WTBL key/rate updates, TX status/free handling, survey/MIB/SCS maintenance, runtime PM workers, DFS radar control, beacon filtering, and firmware coredump assembly.

Important APIs/functions: exports `mt7615_mac_reset_counters()`, `mt7615_mac_set_timing()`, `mt7615_mac_write_txwi()`, `mt7615_mac_wtbl_update()`, `mt7615_mac_sta_poll()`, `mt7615_mac_get_sta_tid_sn()`, `mt7615_mac_set_rates()`, WTBL key setters, `mt7615_rx_check()`, `mt7615_queue_rx_skb()`, `mt7615_mac_set_scs()`, `mt7615_mac_enable_nf()`, `mt7615_mac_cca_stats_reset()`, `mt7615_update_channel()`, PM workers, `mt7615_mac_work()`, `mt7615_tx_token_put()`, DFS init, beacon filter, and `mt7615_coredump_work()`.

Control flow: RX queue entries are classified by packet type. TX status/free packets update tx status, release tokens, clean queues, poll airtime, and reschedule the tx worker. Normal RX packets are decoded from RXD groups, mapped to the correct PHY/WCID, annotated with checksum/decryption/rate/RSSI/AMPDU status, optionally reverse header translation for mesh fragments, and passed to mt76/mac80211. TX path builds TXWI descriptors with queue, WCID, header format, key/protection, fixed-rate, retry, sequence, PID, and beacon flags. MAC work periodically updates survey/MIB counters and SCS sensitivity. DFS setup loads regional radar thresholds through MCU and transitions CAC/active/disabled states.

State and persistence: maintains per-STA rate sets, rate TSF, airtime counters, WCID cipher mask, TX tokens, tx status queues, per-PHY MIB stats, survey time, noise EWMA, false CCA and sensitivity thresholds, DFS state/rdd_state, beacon-filter counts, runtime PM statistics, queued PM SKBs, and coredump message queues. Hardware WTBL and MIB registers are the volatile backing store.

Dependencies and integration: integrates mac80211 RX/TX status APIs, mt76 queue/token/status helpers, connac MCU commands, runtime PM, debug tracepoints, devcoredump, DFS/cfg80211 state, and register definitions from `mac.h`/`regs.h`. `main.c` calls these hooks from mac80211 ops; `mcu.c` supplies command transport.

Risks: RX parsing is length- and flag-sensitive; malformed RXD groups must be rejected to avoid skb overrun. Rate-set TSF selection and asynchronous USB/SDIO rate updates are race-sensitive. WTBL key updates must handle mixed BIP/data ciphers and key index validity correctly. PM work avoids sleeping while the mt76 mutex is held; violating that can break register access. DFS thresholds are regulatory-sensitive.

Test signals: RX traffic with checksum/decryption/radiotap correctness; TX status ACK/retry accounting; AMPDU BA setup/teardown; airtime stats; survey/noise updates; SCS debug values changing under interference; DFS CAC/radar events; beacon filtering for STA/AP roles; token cleanup on reset/unload; devcoredump creation after firmware assert events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mac.h

Purpose: descriptor and MAC bitfield definitions for MT7615-family RXD, RXV, TXD, TXS, DFS radar structures, and WTBL address calculation.

Important APIs/types/macros: defines RX descriptor fields (`MT_RXD*`), RX vector fields (`MT_RXV*`), TX header/packet/port enums, TX descriptor fields (`MT_TXD*`), TX rate fields, TX status fields (`MT_TXS*`), DFS pulse/pattern/spec structs, and `mt7615_mac_wtbl_addr()`.

Control flow: declarative only. The macros are consumed heavily by `mac.c` for parsing hardware RX/TX status and writing TX descriptors, and by `mcu.c` when constructing beacon offload descriptors.

State and persistence: describes volatile packet descriptors and firmware/hardware status formats. DFS structs are in-memory templates passed to MCU radar-threshold commands.

Dependencies and integration: assumes Linux bit macros and `struct mt7615_dev` from included compilation context. WTBL address helper uses `MT_WTBL_BASE(dev)` and `MT_WTBL_ENTRY_SIZE` from register headers.

Risks: descriptor bitfields are hardware ABI. Wrong bit definitions can corrupt TX metadata, misreport RX status, or mis-handle encryption and aggregation. The USB TXD size path in `mac.c` also uses these fields, so changes affect non-MMIO transports.

Test signals: correct RX rate/RSSI/decryption flags, TX descriptor queue selection, TX status retry parsing, DFS pattern commands with expected payload sizes, and WTBL address calculations matching hardware table dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/main.c

Purpose: mac80211 operations implementation for MT7615-family devices, covering radio start/stop, interface and station lifecycle, channel changes, keys, filters, BSS updates, TX, AMPDU, scan/ROC, suspend/resume, antenna, SAR, and TSF operations.

Important APIs/functions: defines and exports `const struct ieee80211_ops mt7615_ops`, plus exported helpers `mt7615_set_channel()`, `mt7615_mac_sta_add()`, `mt7615_mac_sta_remove()`, and `mt7615_tx_worker()`. Internal functions implement add/remove interface, set key, config, WMM conf, filter config, BSS changes, STA rate updates, AMPDU actions, TSF get/set/offset, antenna and coverage class, hardware/scheduled scan, remain-on-channel, decap offload, and PM hooks.

Control flow: start waits for MCU init, powers on required band(s), enables MAC, pushes channel domain/rate power for offload firmware, sets RX path, marks PHY running, schedules MAC work, and resets counters. Stop cancels work/timers, clears running state, cancels scans, disables MAC/PM for bands no longer running. Interface add allocates VIF and OMAC indices, updates DBDC mapping, assigns reserved WTBL entries, and sends dev info to firmware; remove tears down BSS/STA/dev info and masks. Station add/remove allocate/free WTBL WCIDs and firmware records. TX either sends immediately with PM reference or queues skb for wake. Scan/ROC mostly delegate to firmware offload and complete asynchronously from MCU events.

State and persistence: updates `vif_mask`, `omac_mask`, per-PHY `omac_mask`, `monitor_vif`, WCID tables, key indices/cipher state, rx filters, `n_beacon_vif`, scan event queues, ROC state/grant/timer, PM pending SKBs, mac80211 running/suspend/scan bits, station rate cache, and hardware TSF. No durable persistence beyond firmware/hardware state.

Dependencies and integration: integrates with mac80211 callbacks, cfg80211 scan/SAR/ROC/WoWLAN state, mt76 station/tx/status helpers, connac MCU helper library, `mac.c` WTBL/MAC routines, `mcu.c` firmware commands, and init-provided capability/offload decisions.

Risks: OMAC/VIF/WCID allocation has limited table space and must unwind correctly on firmware errors. Key programming falls back for unsupported ciphers and has special MMIE/BIP handling. Runtime PM queuing in TX can reorder wake behavior if not drained correctly. Offload firmware controls availability of scan/ROC/rekey/beacon-filter paths. Suspend/resume must coordinate multiple PHYs.

Test signals: mac80211 interface add/remove across AP/STA/monitor/P2P roles; station association and teardown; hardware encryption for supported ciphers and software fallback for unsupported cases; channel switches with DFS and calibration; AMPDU setup; hardware scan/sched-scan completion; ROC grant/timeout; suspend/resume with WoWLAN when supported; SAR txpower changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mcu.c

Purpose: firmware/MCU command transport, event handling, firmware loading, power ownership, BSS/STA/WTBL command formatting, EEPROM/calibration upload, radar commands, channel/power programming, and offload helpers for MT7615/MT7622/MT7663.

Important APIs/functions: exports `mt7615_mcu_fill_msg()`, `mt7615_mcu_parse_response()`, RF read/write, `mt7622_trigger_hif_int()`, `mt7615_mcu_rx_event()`, `mt7615_mcu_restart()`, `__mt7663_load_firmware()`, `mt7615_mcu_init()`, `mt7615_mcu_exit()`, EEPROM/WMM/DBDC/radar/channel/temperature/test/SKU/calibration/header-translation/BSS-PM/ROC/protection commands. Defines three `mt7615_mcu_ops` tables for WTBL-update, STA-update, and unified offload firmware command styles.

Control flow: command send pushes an MCU TX descriptor, chooses FWDL queue before MCU running and WM queue afterward, and parses responses by sequence and command type. MCU init takes driver ownership, loads chip-specific ROM patch and RAM firmware, sets firmware version and operation table, marks MCU running, optionally applies calibration cache, and disables FW logs. Firmware loading validates trailers, obtains patch semaphore, initializes download regions, sends scatter firmware, starts firmware, and polls ready state. RX events are split between solicited responses and unsolicited scan/ROC/CSA/radar/beacon-loss/BSS-absence/coredump/log events. Higher-level command builders allocate TLV skb payloads for dev/BSS/STA/BA/beacon operations and dispatch through the selected ops table.

State and persistence: persistent inputs are firmware blobs and EEPROM/calibration data. Runtime state includes MCU message sequence/timeout, `fw_ver`, `mcu_ops`, PM ownership bits, `MT76_STATE_MCU_RUNNING`, firmware version string, scan event queues, ROC grants/timers, coredump queues, DBDC mapping, SKU power table, and calibration replay requests. The module parameter `prefer_offload_fw` influences MT7663 firmware selection.

Dependencies and integration: depends on Linux firmware loader, mt76 MCU and connac helper library, `mcu.h` message structures, `mac.h` TXWI construction for beacon offload, `eeprom.h` calibration offsets, regmap for MT7622 wake interrupt, mac80211/cfg80211 notifications, and firmware files declared elsewhere.

Risks: firmware selection changes command ABI; wrong `mcu_ops` table breaks STA/BSS/BA programming. Firmware download relies on trailer size/layout and patch semaphore handling. PM ownership timeouts can wedge the device. Event routing must not free scan/coredump skbs that are queued for later work. Calibration index lookup may fall back to runtime calibration when flash data is missing; wrong frequency mapping can degrade RF performance. Beacon offload has a 512-byte payload limit.

Test signals: firmware version logs and ready-state polling; successful driver-own/firmware-own transitions; BSS/STA creation and BA updates under each firmware mode; scan/ROC events completing mac80211 operations; radar events invoking DFS detection; debugfs RF access and firmware logs; EEPROM upload and channel switch commands; RX DCOC/TX DPD calibration on flash-calibrated devices; coredump generation on firmware assert.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/mcu.c -->
