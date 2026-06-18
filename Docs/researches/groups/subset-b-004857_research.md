# Research: subset-b-004857

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/regs.h

## Purpose
This header is the MT7915/MT7916/MT798x register map for the mt76 `mt7915` family. It defines generation-dependent register descriptor tables, symbolic register offsets, bit fields, queue interrupt masks, WFDMA ring address helpers, MAC/PHY/MIB register blocks, and SoC-only conninfra/ADIE/control registers used by PCI and embedded WMAC variants.

## Important APIs, Types, And Functions
The only C type is `struct mt7915_reg_desc`, which carries `reg_rev`, `offs_rev`, a bus remap table, and map size so runtime code can pick chip-specific addresses. `enum reg_rev` names absolute or base registers that differ by generation, while `enum offs_rev` names per-block offsets for TMAC, MDP, AGG, LPON, MIB, WTBL, PLE, and ETBF. `__REG()` and `__OFFS()` are the core access macros; most later register macros compose through them.

Important register families include `MT_WFDMA0/1`, `MT_MCUQ_RING_BASE`, `MT_TXQ_RING_BASE`, `MT_RXQ_RING_BASE`, interrupt masks such as `MT_INT_RX_DONE_ALL` and `MT_INT_TX_DONE_MCU`, WTBL helpers such as `MT_WTBL_UPDATE` and `MT_WTBL_LMAC_OFFS`, per-band MAC blocks (`MT_WF_TMAC`, `MT_WF_AGG`, `MT_WF_RMAC`, `MT_WF_MIB`, `MT_WF_LPON`), RX filter bits, MIB counters, LED registers, firmware exception registers, and MT798x conninfra/ADIE/AFE/SPI/reset definitions.

## Control Flow
There is no executable control flow, but the header drives control flow elsewhere. Probe code installs the correct `mt7915_reg_desc`; MMIO helpers translate logical names through `__REG` and `__OFFS`; DMA setup uses queue base and interrupt macros; MAC/statistics paths read MIB and WTBL fields; testmode and debug paths manipulate AGG/TMAC/RMAC registers; SoC bring-up uses conninfra, ADIE, SPI, AFE, sleep-protect, and power reset definitions.

## State And Persistence
The file defines persistent hardware state surfaces rather than storing state itself. Most registers describe live device state: DMA enable/reset bits, ring pointers, MCU interrupt status, firmware assert metadata, queue occupancy, WTBL airtime/accounting, MIB counters, RF filters, power ownership, LED state, ADIE calibration fields, and SoC reset/power status. Some counters are clear-on-read and the comments mark DNR counters that firmware should own.

## Dependencies And Integration Points
It depends on kernel bit helpers (`BIT`, `GENMASK`, `FIELD_PREP`) and mt76 queue enums/macros supplied by surrounding headers. It is consumed by mt7915 PCI/MMIO/SoC init, DMA, interrupt, MAC, MCU, debugfs, coredump, LED, and testmode code. The SoC-only definitions are directly coupled to `soc.c` and the MT7981/MT7986 device tree resource model.

## Risks
Address table mistakes are high impact because the same logical macro can resolve differently per generation. Clear-on-read MIB counters can corrupt firmware accounting if polled from the wrong path. Queue index helpers depend on `dev->q_id`, `dev->wfdma_mask`, and interrupt mask arrays being initialized consistently. The register map contains chip-family-specific variants, including MT7916 masks and MT798x ADIE controls, so adding hardware revisions requires careful updates to both enums and backing tables.

## Test Signals
Useful signals include successful DMA ring initialization, interrupts arriving on the expected masks, readable WTBL/MIB counters, correct debugfs/testmode register behavior on both bands, firmware assert dumps using the expected addresses, LED control on supported boards, and MT7981/MT7986 platform boot without SPI, reset, or conninfra timeout errors. Register smoke tests should include both MT7915 and MT7916-style offsets where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/soc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/soc.c

## Purpose
This file provides the platform-driver bring-up path for integrated MT7981/MT7986 WMAC devices using the mt7915 core. It owns SoC resource mapping, reset and clock preparation, conninfra power sequencing, ADIE SPI access/calibration, WED/IRQ setup, and final registration through the common `mt7915_register_device()` path.

## Important APIs, Types, And Functions
The exported platform driver is `mt798x_wmac_driver`, matching `mediatek,mt7981-wmac` and `mediatek,mt7986-wmac`. `mt798x_wmac_probe()` maps MMIO, calls `mt7915_mmio_probe()`, initializes WED/IRQ, calls `mt798x_wmac_init()`, resets wfsys, and registers the common device. `mt798x_wmac_remove()` unregisters it.

The SoC enable/disable API is `mt7986_wmac_enable()` and `mt7986_wmac_disable()`. Supporting helpers include SPI accessors `mt76_wmac_spi_read/write/rmw`, semaphore helpers, conninfra checks/setup, SKU detection and update, GPIO pinctrl selection, ADIE efuse reads, thermal calibration, XTAL trim for 7975/7976 ADIEs, ADIE patch routines, AFE calibration, PLL/clock setup, WFSYS power and WM reset sequencing, and bus-timeout configuration.

## Control Flow
Probe starts with platform resource 0 as the device MMIO window, then delegates common MMIO allocation to mt7915. WED initialization may supply an IRQ; otherwise the platform IRQ is requested. The SoC init path enables named clocks (`mcu`, `ap2conn`), maps DCM/SKU resources, obtains the `consys` reset line, performs a wfsys reset, and registers the common wireless device.

The power-on sequence asserts/deasserts consys reset, selects pinctrl state based on ADIE type, releases conninfra sleep protection, validates conninfra version, programs reserved-memory EMI windows, detects main and optional second ADIE, applies ADIE configuration and calibration, initializes subsystem clocks, wakes WFSYS, powers WM, waits for ROM readiness, and writes SKU decode state. Disable reverses WFSYS power, sleep protection, EMI requests, wakeup, lockup, and reset.

## State And Persistence
Runtime state is stored in `struct mt7915_dev`: mapped `dcm` and `sku` bases, reset controller `rstc`, mt76 device state, WED attachment, and chip id/revision inherited from common code. Hardware state persists in conninfra, WFSYS, AFE, ADIE, SPI, EMI, and reset registers until powered down or reset. Calibration values are read from ADIE efuse and written into analog registers during each setup.

## Dependencies And Integration Points
The file depends on Linux platform, OF, reserved memory, pinctrl, reset, clock, and IRQ APIs. It integrates with mt7915 common MMIO, WED, IRQ handler, firmware registration, and register macros from `regs.h`. Device tree must provide compatible strings, memory resources, reserved memory, pinctrl states (`default` or `dbdc`), clocks, and `consys` reset.

## Risks
The sequencing is timeout-heavy and hardware-order-sensitive. A missing reserved-memory node, wrong pinctrl state, absent clocks, invalid SKU/ADIE combination, or SPI semaphore timeout prevents boot. Several helpers return success even after logging clock lookup failures, so later failures may be harder to attribute. ADIE trim paths use efuse validity flags and chip-specific magic values; regressions can degrade RF behavior without obvious driver errors. Disable paths use best-effort polling and do not propagate all timeout failures.

## Test Signals
Relevant tests are MT7981 and MT7986 probe/remove cycles, firmware boot after `mt7986_wmac_enable()`, suspend or module unload exercising disable, WED IRQ operation, device tree variants for single-band and DBDC ADIEs, ADIE SPI read/write timeout coverage, and RF sanity after thermal/XTAL calibration. Kernel logs should show no conninfra version, ROM index, sleep-protect, reset, or IRQ request failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/soc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/testmode.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/testmode.c

## Purpose
This file implements NL80211 testmode support for MT7915/MT7916. It translates mt76 testmode state and parameters into firmware ATE/RF test commands and direct register programming for factory TX/RX, continuous transmit, frequency offset, TX power, timing, queue cleanup, RX statistics, and temporary register setup.

## Important APIs, Types, And Functions
The public object is `const struct mt76_testmode_ops mt7915_testmode_ops` with `.set_state`, `.set_params`, and `.dump_stats`. Key command helpers are `mt7915_tm_set_tx_power()`, `mt7915_tm_set_freq_offset()`, `mt7915_tm_mode_ctrl()`, `mt7915_tm_set_trx()`, `mt7915_tm_clean_hwq()`, `mt7915_tm_set_slot_time()`, `mt7915_tm_set_tam_arb()`, and `mt7915_tm_set_wmm_qid()`.

State-machine helpers include `mt7915_tm_init()`, `mt7915_tm_set_tx_frames()`, `mt7915_tm_set_rx_frames()`, `mt7915_tm_set_tx_cont()`, `mt7915_tm_set_state()`, and `mt7915_tm_set_params()`. `mt7915_tm_set_ipg_params()` converts requested inter-packet gap/duty timing into SIFS/AIFSN/contention window and TMAC checks. `mt7915_tm_set_tx_len()` derives an SKB payload length from requested TX airtime and rate. `mt7915_tm_reg_backup_restore()` backs up and restores AGG/TMAC/ARB/RMAC registers.

## Control Flow
Entering testmode from OFF calls `mt7915_tm_init()`, which enables SKU control, tells firmware to enter testmode, backs up and relaxes MAC registers, disables normal TX/RX, and creates monitor BSS/STA context. Leaving testmode restores registers, disables arbitration test mode, and returns the monitor station to disconnect state. TX frame mode disables RXV, clears hardware queues, updates channel, computes antenna/SPE, configures TAM arbitration, timing, TX length, and starts MAC TX if an SKB is available. RX frame mode updates channel, clears FCS counters, and enables RX/RXV. Continuous TX switches firmware into RF test mode, programs channel/bandwidth/rate/antenna, and returns to normal RF mode on stop.

## State And Persistence
Per-phy test state lives in `phy->mt76->test` and `phy->test`: last RSSI/RCPI/SNR/frequency offset, `spe_idx`, and `reg_backup`. Register backup memory is devm-allocated and persists for the device lifetime after first use. Hardware state is intentionally mutated while testmode is active and restored when state returns OFF.

## Dependencies And Integration Points
The code depends on mt76 testmode data, cfg80211 bitrate calculation, mt7915 MCU command helpers, MURU control, monitor vif setup, queue/WMM mapping, and register definitions from `regs.h`. It integrates with firmware `MCU_EXT_CMD(ATE_CTRL)`, `TX_POWER_FEATURE_CTRL`, and `RF_TEST` commands.

## Risks
Incorrect state transitions can leave normal MAC TX/RX disabled, test arbitration active, or RF test mode enabled. Register backup is per-band but the backup list is global and must match `TM_REG_MAX_ID`. IPG and TX length calculations can underflow or produce unrealistic queue limits if inputs are inconsistent. Continuous TX rate mapping depends on band rate tables and channel width validation. Antenna mask validation happens in `.set_params`, so stale or out-of-range test parameters can fail late.

## Test Signals
Exercise OFF to IDLE to TX_FRAMES/RX_FRAMES/TX_CONT and back to OFF, including both bands, MT7915 and MT7916 FCS counter masks, HE MU arbitration, duty-cycle derived IPG, explicit TX time, frequency offset, TX power, and invalid bandwidth/rate inputs. After testmode exit, normal association and traffic should recover and direct register dumps should show restored AGG/TMAC/RMAC values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/testmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/testmode.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/testmode.h

## Purpose
This header defines the packed firmware command payloads and local enums used by `testmode.c` for MT7915 ATE and RF test operations. It is the ABI description between the driver testmode path and firmware extended commands.

## Important APIs, Types, And Functions
Important structures are `mt7915_tm_trx`, `mt7915_tm_freq_offset`, `mt7915_tm_slot_time`, `mt7915_tm_clean_txq`, `mt7915_tm_cmd`, `tm_tx_cont`, and `mt7915_tm_rf_test`. `mt7915_tm_cmd` is the generic ATE control wrapper with `testmode_en`, `param_idx`, and a union for parameter-specific payloads. `mt7915_tm_rf_test` is the RF-test wrapper with operation mode, frequency, function index, continuous TX parameters, and padding for firmware expectations.

The enums define MAC TRX modes (`TM_MAC_TX`, `TM_MAC_RX`, `TM_MAC_TXRX`, RXV variants), RF operation modes (`RF_OPER_NORMAL`, `RF_OPER_RF_TEST`, ICAP, overlap, spectrum), and TAM arbitration modes (`TAM_ARB_OP_MODE_NORMAL`, `TEST`, `FORCE_SU`).

## Control Flow
There is no code flow in the header. `testmode.c` fills these structures when changing state, enabling RX/TX, setting slot/frequency/queue cleanup, or switching continuous TX through RF test mode.

## State And Persistence
All structures are transient command buffers. Persistent effects occur only after firmware accepts the commands, where it may alter RF mode, ATE state, MAC TRX gates, timing, and queues until later command reversal.

## Dependencies And Integration Points
The header depends on Linux fixed-width and endian types. It is included by `testmode.c` and must match firmware command layouts for `MCU_EXT_CMD(ATE_CTRL)` and `MCU_EXT_CMD(RF_TEST)`.

## Risks
The structures are `__packed` and field order is firmware ABI. Any padding, size, endian, or enum value change can silently misprogram factory-test firmware. The `test[72]` and `_pad[80]` areas are placeholders for command size compatibility and should not be reused without firmware confirmation.

## Test Signals
Compile-time coverage should verify packed structures remain accepted by firmware. Runtime signals are successful ATE commands for TRX, slot time, queue cleanup, frequency offset, RF mode switching, and continuous TX start/stop without firmware rejects or malformed command traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/testmode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/Kconfig

## Purpose
This Kconfig file declares build-time options for the MT7921 driver family: a shared common module and bus-specific PCIe, SDIO, and USB front ends.

## Important APIs, Types, And Functions
`config MT7921_COMMON` is a tristate selected by concrete transports and selects `MT792x_LIB` plus `WANT_DEV_COREDUMP`. `config MT7921E` enables PCIe support and depends on `MAC80211` and `PCI`. `config MT7921S` enables SDIO support, selects `MT76_SDIO`, and depends on `MAC80211` and `MMC`. `config MT7921U` enables USB support, selects `MT792x_USB`, and depends on `MAC80211` and `USB`.

## Control Flow
Kconfig selection determines which objects in the Makefile are built. Choosing any bus-specific symbol pulls in `MT7921_COMMON`, which builds shared mac80211, MCU, init, MAC, and debugfs logic. Transport options then compile the matching probe/reset/MCU bus implementation.

## State And Persistence
There is no runtime state. The persistent effect is kernel configuration state and module availability.

## Dependencies And Integration Points
This file integrates with the parent mt76 Kconfig tree, mac80211, bus subsystem options, coredump support, and the Makefile in this directory.

## Risks
Missing `select` or `depends on` entries can create link failures or expose unusable menu options. The common symbol is hidden, so all transport options must select it. Optional testmode compilation is controlled elsewhere through `CONFIG_NL80211_TESTMODE` in the Makefile.

## Test Signals
Build matrix signals include `MT7921E=m/y`, `MT7921S=m/y`, `MT7921U=m/y`, combinations of transports, and builds with and without `NL80211_TESTMODE`. `modinfo` should show each bus module and the shared common module as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/Makefile

## Purpose
This Makefile maps MT7921 Kconfig symbols to the shared common module and the PCIe, SDIO, and USB transport modules.

## Important APIs, Types, And Functions
`mt7921-common-y` builds `mac.o`, `mcu.o`, `main.o`, `init.o`, and `debugfs.o`. `mt7921-common-$(CONFIG_NL80211_TESTMODE)` adds `testmode.o`. `mt7921e-y` builds `pci.o`, `pci_mac.o`, and `pci_mcu.o`; `mt7921s-y` builds `sdio.o`, `sdio_mac.o`, and `sdio_mcu.o`; `mt7921u-y` builds `usb.o`.

## Control Flow
Object inclusion follows Kconfig: `CONFIG_MT7921_COMMON` creates `mt7921-common.o`, while each bus symbol creates its own transport object. The bus modules call into exported symbols from the common module for mac80211 ops, RX/TX processing, MCU command helpers, reset work, and device registration.

## State And Persistence
The file stores build composition only. Its runtime effect is module boundaries and exported symbol dependencies.

## Dependencies And Integration Points
It depends on Kbuild syntax, Kconfig symbols from `Kconfig`, and neighboring source files. It also defines whether testmode code participates in common-module builds.

## Risks
Incorrect object membership can cause unresolved symbols or duplicate module definitions. The common module must include all transport-independent exports used by PCI, SDIO, and USB. Optional testmode code must remain guarded by `CONFIG_NL80211_TESTMODE`.

## Test Signals
Build all transport combinations and run `modpost` for unresolved-symbol checks. Testmode builds should expose cfg80211 testmode callbacks, while non-testmode builds should omit `testmode.o` cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/debugfs.c

## Purpose
This file exposes MT7921 diagnostics and developer controls through debugfs. It provides register read/write, firmware logging control, TX statistics, TX power table dumps, runtime PM and deep sleep toggles, chip reset triggering, queue views, PM statistics, and SDIO scheduler quota reporting.

## Important APIs, Types, And Functions
The public entry point is `mt7921_init_debugfs()`. Register access is implemented by `mt7921_reg_get()` and `mt7921_reg_set()` through `fops_regval`. Firmware logging uses `mt7921_fw_debug_get/set()` and calls `mt7921_mcu_fw_log_2_host()`. Power controls are `mt7921_pm_get/set()` and `mt7921_deep_sleep_get/set()`. Reset control is `mt7921_chip_reset()`, which either resets directly or asks firmware to collect a coredump/chip config first. `mt7921_txpwr()` prints rate-indexed user/eeprom/TMAC power limits via `mt7921_get_txpwr_info()`.

## Control Flow
Initialization registers the mt76 debugfs root and conditionally chooses MMIO queue dumping (`mt792x_queues_read`) versus generic queues (`mt76_queues_read`). It adds AC queue, TX power, TX stats, firmware debug, runtime PM, idle timeout, chip reset, runtime PM stats, deep sleep, and SDIO-only scheduler quota files. Setters acquire the mt792x mutex before touching hardware or PM state. Runtime PM toggling wakes the chip, updates user policy, calls `mt7921_set_runtime_pm()`, and reschedules power save.

## State And Persistence
Debugfs values modify live driver state: `dev->fw_debug`, `dev->pm.enable_user`, `dev->pm.ds_enable_user`, `pm->enable`, `pm->ds_enable`, PM timestamps, deep sleep firmware state, and the selected `debugfs_reg` inherited from mt76. The files are transient and disappear when the device is unregistered. Reset may trigger firmware coredump state before hardware reset.

## Dependencies And Integration Points
The code depends on Linux debugfs/seq_file helpers, mt76 debugfs registration, mt792x queue and PM helpers, MCU firmware-log/deep-sleep/chip-config commands, and SDIO scheduler state. It is invoked after common device registration in `init.c`.

## Risks
Debugfs controls bypass normal user policy and can reset the chip or disable power saving. Register writes can corrupt live hardware state. PM setters must avoid USB, where runtime/deep sleep controls return `-EOPNOTSUPP`. Monitor mode blocks deep sleep, so debugfs state and actual firmware state can differ intentionally. TX power dump formatting assumes firmware event layout matches `struct mt7921_txpwr`.

## Test Signals
Read/write `regidx`/`regval`, toggle `fw_debug`, `runtime-pm`, `deep-sleep`, and `idle-timeout`, read TX power and queue files on PCI/SDIO/USB variants, trigger chip reset with and without coredump collection, and validate SDIO `sched-quota` appears only for SDIO. Lockdep should not report mutex inversions during debugfs operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/init.c

## Purpose
This file initializes MT7921 common hardware and mac80211 registration. It handles thermal hwmon exposure, regulatory domain updates, MAC hardware setup, firmware/eeprom init retry, asynchronous common device registration, power-save defaults, wiphy capability tweaks, workqueue setup, and stream capability publication.

## Important APIs, Types, And Functions
The exported registration function is `mt7921_register_device()`. It initializes `struct mt792x_dev` and `struct mt792x_phy` members, work items, wait queues, PM state, ACPI SAR, WCID table, wiphy, regulatory notifier, HT/VHT/HE capabilities, antenna availability, and queues `mt7921_init_work()`.

Hardware helpers include `mt7921_mac_init()`, `__mt7921_init_hardware()`, and `mt7921_init_hardware()`. Regulatory helpers are `mt7921_regd_update()`, `mt7921_regd_notifier()`, and `mt7921_regd_channel_update()`. Thermal support is implemented by `mt7921_thermal_temp_show()` and `mt7921_thermal_init()`.

## Control Flow
Transport probe calls `mt7921_register_device()`, which prepares software state and queues asynchronous init work. `mt7921_init_work()` retries firmware/eeprom/MAC initialization through `mt7921_init_hardware()`, sets stream and HE capabilities, configures MAC addresses, registers the mt76 device with mac80211, initializes debugfs, registers hwmon temperature input, marks `hw_init_done`, and applies initial deep sleep state.

Hardware init forces `MT_SWDEF_MODE` to normal, runs bus-specific MCU init through `mt792x_mcu_init()`, applies EEPROM overrides, sends EEPROM mode to firmware, and initializes MAC registers. Regulatory notifications update alpha2/DFS/environment, optionally set country-IE ignore behavior, skip work while suspended, then push CLC, channel-domain, and SAR power changes under the driver mutex.

## State And Persistence
The file initializes persistent driver state: PM work and flags, reset/init/scan/coredump/ROC work, IPv6 NS queue, scan/coredump queues, wait queues, `pm.idle_timeout`, country/region fields, `regd_in_progress`, thermal hwmon device, and hardware initialization state. Regulatory channel-disable decisions persist in wiphy channel flags until rebuilt. Firmware state includes EEPROM buffer mode, MDP/MAC config, channel domain, CLC, SAR power, and deep sleep.

## Dependencies And Integration Points
It depends on mac80211/cfg80211, hwmon, firmware, ACPI SAR, mt792x common helpers, mt76 EEPROM override, MCU helpers from `mcu.c`, MAC helpers from `mac.c`, debugfs, coredump, and transport-specific HIF ops installed before registration.

## Risks
Registration is asynchronous, so remove paths must cancel `init_work`. Hardware init retry relies on transport reset hooks being safe before full registration. Regulatory updates race with suspend and are guarded by `regd_in_progress`; suspend paths wait for that flag. Channel disabling combines CLC firmware data and device tree power-limit nodes, so missing or wrong DT entries can disable bands. hwmon temperature reads call firmware under the mutex and may fail during reset/suspend.

## Test Signals
Probe on PCI/SDIO/USB, firmware init retry after injected failure, mac80211 registration, debugfs/hwmon creation, temperature reads, regulatory alpha2 changes, country IE handling, 5/6 GHz channel disabling, SAR updates, and suspend while regulatory update is in flight. `hw_init_done` should become true only after full registration and debugfs/thermal setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/mac.c

## Purpose
This file implements MT7921 MAC data-path support shared by PCI, SDIO, and USB. It parses RX descriptors, dispatches MCU events and TX status/free notifications, updates station airtime/rate/RSSI data from WTBL, handles chip reset and coredump work, and provides USB/SDIO TX descriptor preparation/completion helpers.

## Important APIs, Types, And Functions
Exported entry points include `mt7921_mac_wtbl_update()`, `mt7921_rx_check()`, `mt7921_queue_rx_skb()`, `mt7921_mac_reset_work()`, `mt7921_coredump_work()`, `mt7921_usb_sdio_tx_prepare_skb()`, `mt7921_usb_sdio_tx_complete_skb()`, and `mt7921_usb_sdio_tx_status_data()`. Internal core helpers include `mt7921_mac_sta_poll()`, `mt7921_mac_fill_rx()`, `mt7921_mac_add_txs()`, `mt7921_mac_tx_free()`, and `mt7921_vif_connect_iter()`.

## Control Flow
RX enters through `mt7921_queue_rx_skb()` or `mt7921_rx_check()`. Packet type selects TX free processing, TX status parsing, MCU event handling, or normal RX descriptor parsing. Normal RX validation rejects wrong band, non-running state, malformed A-MSDU/header translation cases, descriptor length errors, and unsupported rate parse results. Valid frames receive status metadata, checksum state, decryption flags, RSSI/rate/radiotap data, A-MPDU sequence info, and are passed to `mt76_rx()`.

TX free notifications clean DMA queues, release mt76 tokens, update retry/failure counters, free TXWIs, schedule TX worker, and poll stations. Reset work stops queues, cancels PM work, retries `mt792x_dev_reset()`, aborts scans if needed, wakes queues, reconnects active interfaces through MCU dev/BSS/STA/beacon commands, and reschedules power save. Coredump work aggregates queued firmware assert fragments before calling `dev_coredumpv()` and resetting.

## State And Persistence
State includes per-WCID airtime counters, rate info, average ACK signal, TX token idr, reset flags (`MT76_RESET`, `hw_full_reset`, `fw_assert`), scan state, coredump message queues, IPv6 NS queue, and PM queues. Hardware state includes WTBL counters, RX/TX descriptors, DMA queues, firmware assert data, beacon offload, BSS contexts, and station contexts rebuilt after reset.

## Dependencies And Integration Points
The code integrates mt76 DMA/token/RX/TX helpers, mac80211 RX status APIs, connac2 descriptor formats, MCU event code from `mcu.c`, common mt792x reset/PM helpers, coredump framework, and transport driver ops. USB/SDIO helpers are used by SDIO and USB modules; PCI uses `pci_mac.c`.

## Risks
RX descriptor parsing is length-sensitive and mixes header-translated and 802.11 paths; mistakes can corrupt SKBs or radiotap metadata. TX free parsing increments count when encountering WCID pairs and must stay within event bounds. Reset recovery does not fully replay all mac80211 state itself, so ordering with mac80211 queues, scans, PM, and firmware restart matters. Coredump aggregation drops excess data silently when exceeding the fixed dump size. USB/SDIO pad/headroom errors must release packet IDs.

## Test Signals
Test normal RX, monitor RX, header translation, fragmented encrypted frames, A-MSDU, checksum offload, HE radiotap, TX status and TX free events, airtime accounting, reset during scan and traffic, firmware coredump generation, USB/SDIO TX headroom/padding, and IPv6 NS offload work. KASAN, lockdep, and skb bounds diagnostics are important for this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/main.c

## Purpose
This file is the MT7921 mac80211 operation layer. It advertises HE capabilities, starts/stops the device, manages interfaces, keys, station state, channel contexts, scans, remain-on-channel, power-save policy, filters, AP mode, SAR, suspend/resume, IPv6 neighbor solicitation offload, channel switch, and rfkill polling.

## Important APIs, Types, And Functions
The central exported object is `const struct ieee80211_ops mt7921_ops`. Shared exports include `mt7921_set_stream_he_caps()`, `__mt7921_start()`, `mt7921_roc_abort_sync()`, `mt7921_set_channel()`, `mt7921_set_runtime_pm()`, `mt7921_mac_sta_add()`, `mt7921_mac_sta_event()`, `mt7921_mac_sta_remove()`, `mt7921_scan_work()`, and `mt7921_set_tx_sar_pwr()`.

Major callback helpers include `mt7921_start/stop`, `mt7921_add_interface`, `mt7921_set_key`, `mt7921_config`, `mt7921_configure_filter`, `mt7921_bss_info_changed`, `mt7921_start_ap/stop_ap`, `mt7921_ampdu_action`, scan/sched-scan helpers, suspend/resume, decap offload, channel context callbacks, managed prepare/complete TX ROC, CSA work/timers, and `mt7921_rfkill_poll()`.

## Control Flow
Start enables MAC firmware, sets channel domain, programs RX path, applies SAR power, resets counters, schedules watchdog work, controls LEDs on MMIO, and starts rfkill polling if firmware supports RF pin events. Interface add allocates an mt76 vif index, adds a firmware dev context, reserves a WCID, initializes WMM and beacon-filter flags, and sets CSA work/timer. BSS changes update slot timing, beacon filter/power-save, association, ERP/EDCA, beacon offload, RSSI monitor, and power state through MCU helpers.

Station add allocates WCIDs and optional WEP station state. Association events add BSS context for station mode, clear WTBL counters, and push station records. Removal aborts ROC, frees pending TX, removes firmware station/BSS state, clears poll list/RSSI, and updates 6 GHz power type. ROC uses a token, waits for firmware grant, arms a timer, and aborts on cancellation or expiry. Channel switching stores `new_ctx`, arms a CSA timer, and applies the new context in work.

## State And Persistence
State spans vif masks, OMAC masks, per-vif WCIDs, WMM index, CSA timer/work, ROC token/grant/timer, scan event list, PM policy bits, beacon-filter flags, monitor/sniffer mode, antenna/chain masks, SAR power, channel context pointers, and per-station aggregation state. Firmware state includes dev/BSS/STA records, keys, BA sessions, channel context, beacon offload, RX filters, sniffer config, RSSI monitor, ROC, and suspend/offload settings.

## Dependencies And Integration Points
The file is tied to mac80211/cfg80211 callbacks, mt76 core station/key/channel helpers, connac MCU commands, `mcu.c`, `mac.c`, mt792x shared PM/reset helpers, ACPI SAR, IPv6, and transport-specific HIF operations.

## Risks
Many callbacks run under the driver mutex and interact with PM wake/sleep; missing wake protection can race firmware sleep. Key deletion intentionally skips some station-mode reassociation cases, which can leave stale firmware keys if disconnect ordering changes. ROC and CSA timers must be canceled on teardown. Channel context handling stores a single `dev->new_ctx`, so concurrent contexts require care. Monitor mode disables runtime/deep sleep and beacon filtering. Station AID is capped at `MT7921_MAX_AID`.

## Test Signals
Cover station/AP/monitor interface lifetimes, WPA/WEP/IGTK keys, association/disassociation, BA start/stop, hardware scan and sched scan, ROC and managed join offchannel, channel switch, SAR/regulatory updates, suspend/resume with GTK rekey, IPv6 NS offload, antenna changes, rfkill polling, beacon offload, and monitor/sniffer toggling. Firmware logs should show matching DEV/BSS/STA/ROC/BA commands and no stale timers after remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/mcu.c

## Purpose
This file implements MT7921 firmware command and event handling. It parses MCU responses, routes unsolicited events, loads CLC data from firmware, queries NIC capabilities, starts firmware, configures EDCA/ROC/channel/eeprom/power-save/beacon filtering/stations/sniffer/beacon offload/CLC/thermal/RF pin/RX filters/RSSI monitor, and provides suspend IPv6 offload glue.

## Important APIs, Types, And Functions
Key exports are `mt7921_mcu_parse_response()`, `mt7921_mcu_set_suspend_iter()`, `mt7921_mcu_rx_event()`, `mt7921_mcu_uni_tx_ba()`, `mt7921_mcu_uni_rx_ba()`, `mt7921_run_firmware()`, `mt7921_mcu_radio_led_ctrl()`, `mt7921_mcu_set_tx()`, `mt7921_mcu_set_roc()`, `mt7921_mcu_abort_roc()`, `mt7921_mcu_set_chan_info()`, `mt7921_mcu_set_eeprom()`, `mt7921_mcu_uni_bss_ps()`, `mt7921_mcu_set_bss_pm()`, `mt7921_mcu_sta_update()`, `mt7921_mcu_set_beacon_filter()`, `mt7921_get_txpwr_info()`, `mt7921_mcu_set_sniffer()`, `mt7921_mcu_config_sniffer()`, `mt7921_mcu_uni_add_beacon_offload()`, `mt7921_mcu_set_clc()`, `mt7921_mcu_get_temperature()`, `mt7921_mcu_wf_rf_pin_ctrl()`, `mt7921_mcu_set_rxfilter()`, and `mt7921_mcu_set_rssimonitor()`.

## Control Flow
Responses are parsed by command type; timeouts log and reset the device, sequence mismatches return `-EAGAIN`, and selected commands extract status fields. RX MCU events are separated into UNI unsolicited events, legacy unsolicited events, and normal command responses. Events trigger ROC grants, scan completion queueing, connection-loss notification, firmware debug logging, coredump collection, low-power trace events, TX done processing, and CQM RSSI notifications.

Firmware run loads firmware, queries NIC capabilities, loads CLC data from the firmware trailer, marks MCU running, and enables firmware logs. CLC loading scans non-download firmware regions, stores matching CLC blobs, and submits country/environment rules with fallback to alpha2 `00`. Channel, ROC, EDCA, beacon, station, and power-save helpers build packed MCU payloads from mac80211 vif/channel/station state.

## State And Persistence
The file mutates `dev->phy.clc[]`, `dev->phy.clc_chan_conf`, chip capability flags, chainmask/antenna capabilities, 6 GHz support, MAC address, SDIO scheduler quota, firmware logging state, `MT76_STATE_MCU_RUNNING`, ROC grant/timer state, coredump state, RSSI/CQM delivery, and firmware-side BSS/STA/channel/filter/offload state.

## Dependencies And Integration Points
It depends on mt76 MCU queues, connac/connac2 command formats, firmware trailer structures, cfg80211/mac80211 state, coredump support, tracepoints, ACPI/DT power-limit helpers, SDIO scheduler state, and helpers from `mac.c` and `main.c`.

## Risks
Firmware ABI packing is dense and command-specific; field or endian mistakes cause subtle firmware failures. Response parsing resets the device on timeout, so spurious timeout handling has high blast radius. CLC parsing trusts trailer region lengths after bounds checks and must avoid reinitializing buffers across chip reset. ROC grant handling assumes event TLV layout and request type. Beacon offload has a 512-byte payload limit. RX event routing must free or retain SKBs exactly once.

## Test Signals
Test firmware download, NIC capability parsing, CLC disabled/enabled/fallback flows, country updates, EDCA and MU EDCA, ROC grant/abort, channel switch reasons, eeprom mode, BSS PM and beacon filtering, station records, BA commands, TX power query, sniffer config, beacon offload size limits, thermal query, RF pin rfkill polling, RX filter changes, RSSI monitor events, coredump events, scan events, and command timeout recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/mcu.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/mcu.h

## Purpose
This header defines MT7921-specific MCU event, command, testmode, CLC, TX power, and RF-pin payload structures and constants used by `mcu.c`, `debugfs.c`, and testmode code.

## Important APIs, Types, And Functions
Important structures include `mt7921_mcu_tx_done_event`, `mt7921_mcu_eeprom_info`, `mt7921_mcu_ant_id_config`, `mt7921_txpwr_req`, `mt7921_txpwr_event`, `mt7921_wf_rf_pin_ctrl_event`, `mt7921_rftest_cmd`, `mt7921_rftest_evt`, and `mt7921_clc_info_tlv`. Constants define the rate encoding masks (`MT_RA_RATE_*`), beamforming flags, rate report event id, RF test modes, and CLC channel-conf bitmap meaning.

## Control Flow
There is no executable flow. `mcu.c` casts firmware SKB data to these structures while parsing TX done, EEPROM, TX power, RF pin, RF test, and CLC response/event payloads.

## State And Persistence
All structures are transient host-side views of firmware messages. Persistent effects are held in firmware and driver fields updated from those messages, such as TX power tables, CLC channel configuration, RF pin result, and TX status.

## Dependencies And Integration Points
The header includes `mt76_connac_mcu.h` and references `MT7921_EEPROM_BLOCK_SIZE`, `struct mt7921_txpwr`, and common connac MCU formats. It is included by MT7921 common MCU/debug/test paths.

## Risks
Packed layout mismatches break firmware communication. The TX done event includes fixed-size reserved and TXS regions; consumers assume `txs` starts at the expected offset. CLC channel-conf comments are the contract used by regulatory channel disabling, so bit interpretation must stay synchronized with firmware.

## Test Signals
Signals include successful TX done parsing, EEPROM block reads, TX power debugfs dumps, RF pin ctrl responses, RF test commands, and CLC event parsing on firmware revisions that report UNII channel configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/mcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/mt7921.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/mt7921.h

## Purpose
This is the central MT7921 common header. It declares chip constants, firmware event ids, ROC enums, SDIO interrupt layout, EEPROM/CLC/TX power structures, queue and ring sizing, DMA layout details, inline L1 remap register helpers, and cross-file function prototypes for common, PCI, SDIO, USB, MCU, MAC, debugfs, testmode, PM, and regulatory code.

## Important APIs, Types, And Functions
Key constants define AID limit, TX/RX/MCU ring sizes, EEPROM sizes, token count, CLC event ids, LED control ids, RF pin actions, and queue ids. Structures include `mt7921_realease_info`, `mt7921_fw_features`, `mt7921_roc_grant_tlv`, `mt7921_sdio_intr`, `mt7921_dma_layout`, `mt7921_clc_rule`, `mt7921_clc`, and `mt7921_txpwr`.

The header declares `extern const struct ieee80211_ops mt7921_ops` and exports prototypes for registration, firmware, channel, MCU command helpers, MAC RX/TX/reset functions, debugfs, PCI/SDIO HIF helpers, USB/SDIO TX helpers, SAR, CLC, ROC, and RSSI monitor. Inline helpers `mt7921_reg_map_l1()`, `mt7921_l1_rr/wr/rmw()`, `mt7921_l1_set()`, and `mt7921_l1_clear()` handle remapped register access.

## Control Flow
The header defines call surfaces rather than flow. Transport probes install bus/HIF ops and call `mt7921_register_device()`. The common code references prototypes here to wire mac80211 callbacks, MCU commands, reset work, debugfs, and transport-specific reset/MCU control.

## State And Persistence
The declarations describe persistent driver state located in `struct mt792x_dev` and `struct mt792x_phy` from the shared mt792x layer, plus firmware-visible state represented by EEPROM, CLC, ROC, TX power, SDIO interrupt, and DMA layout structures.

## Dependencies And Integration Points
It includes `../mt792x.h` and `regs.h`, making it the bridge from the mt792x common library to MT7921-specific files. It is consumed by all files in the directory and by bus modules that need shared exports.

## Risks
Prototype drift creates link or ABI mistakes across modules. Constants such as ring sizes, token size, queue ids, and EEPROM offsets must match firmware and hardware. L1 remap helpers mutate a shared remap register and require serialized access through normal mt76 register locking. The misspelled `mt7921_realease_info` type appears ABI-like and should not be renamed casually if referenced elsewhere.

## Test Signals
Build coverage across PCI/SDIO/USB and testmode validates declarations. Runtime signals include correct L1 remapped reads, SDIO interrupt parsing against `mt7921_sdio_intr`, queue id use in DMA setup, CLC regulatory behavior, and TX power debugfs parsing of `mt7921_txpwr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/mt7921.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/pci.c

## Purpose
This file is the PCIe transport driver for MT7921/MT7922/MT7920/MT7902. It owns PCI device matching, MMIO setup, register address remapping, DMA queue initialization, IRQ map setup, ASPM policy, probe/remove, PCI suspend/resume, and module metadata.

## Important APIs, Types, And Functions
The module entry is `module_pci_driver(mt7921_pci_driver)`. The core callbacks are `mt7921_pci_probe()`, `mt7921_pci_remove()`, `mt7921_pci_suspend()`, `mt7921_pci_resume()`, and `mt7921_pci_shutdown()`. Register access is wrapped by `__mt7921_reg_addr()`, `mt7921_rr()`, `mt7921_wr()`, and `mt7921_rmw()`. DMA setup is in `mt7921_dma_init()`. Unregistration cleanup is in `mt7921e_unregister_device()`.

## Control Flow
Probe enables PCI, ensures memory decoding, allocates an IRQ vector, sets a 32-bit DMA mask, optionally disables ASPM, gets mac80211 ops from firmware feature metadata, allocates mt76 device state, maps BAR0, initializes MMIO, installs mutable bus ops that remap logical register addresses, takes firmware/driver ownership, reads chip revision, resets WFSYS, masks interrupts, requests IRQ, initializes DMA rings, and calls `mt7921_register_device()`.

`mt7921_dma_init()` selects a DMA layout, with MT7902 using MCU TXQ 15, a larger shared MCU RX ring, and no MCU_WA ring. It attaches DMA, disables WPDMA, allocates data, MCU, firmware-download, and RX queues, enables NAPI, and enables DMA. Suspend cancels PM/reset/ROC work, takes driver ownership, waits for regulatory updates, turns off LED, suspends HIF, forces deep sleep, disables NAPI/workers/DMA/interrupts, and gives ownership to firmware. Resume reverses ownership, DMA/IRQ/NAPI/workers, HIF suspend, regulatory update, and LED.

## State And Persistence
State includes PCI drvdata, `dev->fw_features`, HIF ops, IRQ map, bus ops, ASPM support flag, MMIO register remap state, revision, DMA queues, IRQ tasklet, NAPI state, PM suspend flag, wakeup-source flag, and MCU response queue. Hardware state includes WFDMA rings, interrupt masks, PCI MAC interrupt enable, HIF suspend state, deep sleep, LED state, and ownership registers.

## Dependencies And Integration Points
It depends on Linux PCI, OF wakeup-source property, mt76 MMIO/DMA/PCI helpers, mt792x HIF helpers, `pci_mac.c`, `pci_mcu.c`, and common MT7921 registration/RX/TX callbacks.

## Risks
Register remap mistakes can make unsupported addresses return zero after logging, leading to failed hardware operations. MT7902 special cases must keep IRQ map and DMA layout consistent. Suspend/resume ordering is sensitive to regulatory work, DMA idle polling, IRQ tasklet shutdown, and firmware ownership. Error paths must free IRQ vectors and mt76 device without double-freeing managed BAR mappings. ASPM policy can affect stability.

## Test Signals
Probe all listed PCI IDs, verify chip revision and firmware choice, run traffic on MT7921/MT7922/MT7920/MT7902, exercise reset, suspend/resume, wakeup-source, ASPM disabled/enabled, DMA queue allocation failure paths, interrupt masks, and register debugfs reads across remapped address ranges. Check no NAPI/tasklet use after remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/pci_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/pci_mac.c

## Purpose
This file contains PCIe-specific TX preparation and MAC reset recovery for MT7921. It handles TXWI/HW TXP creation for DMA tokens and performs a full PCI/WPDMA-oriented firmware/MAC restart after reset.

## Important APIs, Types, And Functions
`mt7921e_tx_prepare_skb()` is the PCI driver-op TX prepare callback. It allocates a mt76 token, requests periodic TX status for stations, writes the connac2 TXWI, writes the hardware TXP descriptor, and hands SKB ownership to DMA. `mt7921e_mac_reset()` is the PCI HIF reset callback used by reset work.

## Control Flow
TX prepare rejects too-short frames, defaults missing WCID to global WCID, stores the SKB in the TXWI cache area, consumes a token, optionally requests status once per station per quarter-second, allocates a packet-status id, writes TXWI and HW TXP, and nulls `tx_info->skb` so the caller knows DMA owns it.

Reset takes driver ownership, frees pending TX, disables host and PCI MAC interrupts, marks MCU reset, wakes MCU waiters, purges responses, schedules TX queues, disables TX worker and NAPI, frees tokens, resets the token idr, resets WPDMA, re-enables RX NAPI, clears firmware assert/MCU reset, restores interrupts, takes driver ownership again, runs firmware, sets EEPROM, initializes MAC, starts the PHY, and finally re-enables TX NAPI and TX worker.

## State And Persistence
TX state includes mt76 tokens, packet ids, TXWI cache entries, station `last_txs`, and DMA descriptors. Reset state includes interrupt masks, NAPI enablement, worker state, MCU reset bit, response queue, token idr, `fw_assert`, firmware running state, EEPROM/MAC state, and running PHY state.

## Dependencies And Integration Points
It depends on mt76 DMA/token helpers, connac2 TXWI/TXP helpers, PCI interrupt registers from `regs.h`, firmware and MAC init from common code, and HIF ownership helpers from `pci_mcu.c`/mt792x.

## Risks
Token ownership is delicate: failures after token consume must be unwound by later layers or avoided. Reset temporarily disables many asynchronous paths and must re-enable NAPI/workers even when firmware init fails. Reinitializing the token idr while SKBs are still referenced would corrupt completions, hence pending TX cleanup comes first. Interrupt masks must match the PCI probe IRQ map, including MT7902 differences.

## Test Signals
Transmit on all ACs, management frames, encrypted frames, aggregation setup, status reporting cadence, token exhaustion, and reset under traffic. After reset, firmware should rerun, MAC init should succeed, queues should wake, and TX/RX should resume without token leaks or stuck NAPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/pci_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/pci_mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/pci_mcu.c

## Purpose
This file provides PCIe-specific MCU ownership and message transport for MT7921. It installs MCU ops, moves the device from firmware ownership to driver ownership, disables PCI L0s, runs firmware, and routes firmware-download commands to the firmware-download queue.

## Important APIs, Types, And Functions
`mt7921e_driver_own()` writes `MT_TOP_LPCR_HOST_DRV_OWN` and polls for firmware ownership to clear. `mt7921_mcu_send_message()` fills a connac2 MCU TX descriptor, sets timeout to three seconds, selects `MT_MCUQ_FWDL` for `MCU_CMD(FW_SCATTER)` and `MT_MCUQ_WM` otherwise, then sends the raw SKB to the selected MCU queue. `mt7921e_mcu_init()` installs `mt76_mcu_ops` and runs ownership plus firmware load.

## Control Flow
During PCI probe or reset, common mt792x MCU init calls `mt7921e_mcu_init()`. The function installs `.mcu_skb_send_msg` and `.mcu_parse_response`, takes driver ownership, disables PCI L0s in `MT_PCIE_MAC_PM`, runs firmware through common `mt7921_run_firmware()`, and cleans the firmware-download queue.

## State And Persistence
State changes include host/firmware ownership, MCU operation table pointer, MCU timeout, PCI power-management register L0s disable bit, firmware running state set by common code, and firmware-download queue contents.

## Dependencies And Integration Points
It depends on PCI register remap helpers, mt76 MCU ops, connac2 message filling, raw TX queue submission, and `mt7921_mcu_parse_response()`/`mt7921_run_firmware()` from common MCU code.

## Risks
Ownership polling failure prevents all later firmware communication. Queue selection must send scatter download commands to the FWDL queue, or firmware download stalls. The hardcoded timeout affects all PCI MCU commands. Disabling L0s is hardware-specific and should stay aligned with PCI power behavior.

## Test Signals
Probe and reset should show successful driver ownership, firmware scatter download on FWDL, normal MCU commands on WM, no timeout during firmware start, and a cleaned FWDL queue after init. Inject ownership timeout to verify `-EIO` and cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/pci_mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/regs.h

## Purpose
This header defines the compact MT7921-specific register map used by common and PCI/SDIO/USB code. It extends shared `mt792x_regs.h` with MDP, WFDMA interrupt, HIF L1 remap, WTBL update, and WFSYS reset registers.

## Important APIs, Types, And Functions
There are no functions or types. Important macros include `MT_MDP_DCR0/DCR1` and fields for D-AMSDU and RX header translation, per-band RX filter routing registers `MT_MDP_BNRCFR0/1`, host interrupt enable `MT_WFDMA0_HOST_INT_ENA`, TX/RX interrupt masks (`MT_INT_RX_DONE_*`, `MT_INT_TX_DONE_*`), `MT_RX_DATA_RING_BASE`, L1 remap fields (`MT_HIF_REMAP_L1*`), `MT_WFSYS_SW_RST_B`, `MT_WTBL_UPDATE`, and `MT_WTBL_UPDATE_ADM_COUNT_CLEAR`.

## Control Flow
The macros are consumed by MAC init, RX filter setup, DMA/interrupt setup, PCI remap helpers, WTBL counter clearing, and reset code. `mt7921_reg_map_l1()` in `mt7921.h` uses the L1 remap definitions to access high physical addresses.

## State And Persistence
The header names hardware state rather than storing state. The related hardware state includes MDP RX behavior, host interrupt enables, DMA ring bases, remap window selection, WFSYS reset latch, WTBL admin counters, and WTBL update busy state.

## Dependencies And Integration Points
It includes the shared mt792x register header and is included by `mt7921.h`. It integrates with `init.c`, `main.c`, `mac.c`, `mcu.c`, `pci.c`, and bus-specific reset code.

## Risks
Interrupt-mask or ring-base mistakes break RX/TX completions. L1 remap definitions are shared mutable register state and require serialized access. The file is much smaller than `mt7915/regs.h`, so unsupported blocks must come from shared `mt792x_regs.h`; adding direct MT7921 register users should avoid duplicating shared definitions.

## Test Signals
MAC init should set MDP fields correctly, interrupts should fire for data/MCU/FWDL queues, WTBL counter clearing should complete, L1 remap register reads should return chip ids/revisions, and reset code should manipulate WFSYS registers without unsupported address errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/sdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/sdio.c

## Purpose
This file is the SDIO transport driver for MT7921S and MT7902 SDIO devices. It owns SDIO device matching, bus initialization, interrupt parsing, RX/TX queue setup, SDIO worker PM gating, common device registration, remove, suspend/resume, and module metadata.

## Important APIs, Types, And Functions
The module entry is `module_sdio_driver(mt7921s_driver)`. Core callbacks are `mt7921s_probe()`, `mt7921s_remove()`, `mt7921s_suspend()`, and `mt7921s_resume()`. `mt7921s_txrx_worker()` wraps the generic SDIO TX/RX worker with mt76 connac PM references. `mt7921s_unregister_device()` performs cleanup. `mt7921s_parse_intr()` reads and validates SDIO interrupt status into generic `struct mt76s_intr`.

## Control Flow
Probe obtains mac80211 ops based on firmware metadata, allocates an mt76 device with SDIO-oriented driver ops, installs HIF ops, initializes the SDIO bus and hardware, reads ASIC revision, installs interrupt parser and interrupt data buffer, allocates main and MCU RX queues plus TX resources, creates the SDIO txrx worker with FIFO scheduling, and calls `mt7921_register_device()`.

The txrx worker takes a PM reference; if the device is asleep it queues wake work and returns, otherwise it runs `mt76s_txrx_worker()` and drops the PM reference. Interrupt parsing claims the SDIO host, reads `MCR_WHISR` into `mt7921_sdio_intr`, rejects impossible RX counts, and exposes ISR/mailbox/TX quota/RX length arrays. Suspend marks PM suspended, sets `MT76_STATE_SUSPEND`, cancels PM/reset/ROC work, takes driver ownership, forces deep sleep, drains TX queues, suspends HIF, disables SDIO workers, gives firmware ownership, and asks MMC to keep power. Resume clears suspend state, takes driver ownership, re-enables workers, restores deep sleep if needed, clears HIF suspend, and resets on failure.

## State And Persistence
State includes SDIO drvdata, `fw_features`, HIF ops, bus ops, interrupt buffer, SDIO wait queue, txrx/status/stat/net workers, PM suspend flag, suspend state bit, bus_hung flag, revision, SDIO scheduler quotas populated by MCU capability parsing, and RX/TX queues. Hardware state includes SDIO function registers, HIF suspend state, deep sleep, firmware/driver ownership, and retained MMC power during suspend.

## Dependencies And Integration Points
It depends on Linux MMC/SDIO APIs, mt76 SDIO core, common MT7921 mac80211/MAC/MCU functions, SDIO reset/MCU helpers in `sdio_mac.c`/`sdio_mcu.c`, and mt792x PM helpers.

## Risks
Interrupt parsing is layout-sensitive; invalid RX counts are rejected to avoid overruns. Worker PM gating can starve TX/RX if wake work fails. Suspend requires all TX queues to empty before HIF suspend; timeout or worker ordering mistakes can hang resume. Error paths call `mt76s_deinit()` and `mt76_free_device()` before registration, while registered removal uses `mt7921s_unregister_device()`.

## Test Signals
Probe MT7921 and MT7902 SDIO IDs, parse interrupts with RX count limits, run traffic through PM sleep/wake cycles, suspend/resume with MMC keep-power, drain TX queues, remove during init failure, and validate reset on resume/suspend failures. Debugfs `sched-quota` should reflect SDIO scheduler data after NIC capability parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7921/sdio.c -->
