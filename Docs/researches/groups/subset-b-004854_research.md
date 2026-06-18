# Research: subset-b-004854

Grouped report for `subset-b-004854`, covering MediaTek mt76x0 USB, shared mt76x02, and mt76x2 PCI/USB integration files. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/usb.c

Purpose: USB bus driver for MT7610U/MT7630U/MT7650U adapters. It binds a vendor/product table, allocates the shared `mt76x02_dev`, wires mac80211 operations to the mt76x02 common helpers, initializes USB queues, firmware, hardware, beacons, and power-management callbacks.

Important APIs/types/functions: `mt76x0u_probe()`, `mt76x0u_register_device()`, `mt76x0u_init_hardware()`, `mt76x0u_start()`, `mt76x0u_stop()`, suspend/resume, and `mt76x0u_ops`. Driver ops point TX/RX, station, channel, survey, and status handling at shared mt76x02 code while using USB-specific `mt76x02u_tx_prepare_skb()` and completion.

Control flow: probe enables and resets USB, initializes MCU transport, disables hardware after hot reboot, validates ASIC/eFUSE, then registers the device. Register allocates USB queues, powers the chip, loads MCU firmware, initializes common hardware and beacon timers, then calls mt76x0 registration. Start enables MAC/RX/TX and schedules calibration/MAC work; stop cancels work, stops USB TX, tears down beacon timers, polls DMA idle, and stops MAC.

State and persistence: persistent state is kernel device state, `mphy.state` bits, USB queue allocation, `no_2ghz` Archer T1U quirk, firmware state, beacon timer state, and calibration work scheduling. No user-space persistence is written.

Dependencies/integration: integrates Linux USB core, mac80211, mt76 USB helpers, mt76x0 chip/PHY code, mt76x02 common TX/RX/beacon/util/debug helpers, and firmware files `mt7610e.bin`/`mt7610u.bin`.

Risks: hot-reboot MCU readiness, DMA busy polling, USB device lifetime balance, unsupported ASIC IDs, quirk-limited bands, and cleanup paths before `MT76_STATE_INITIALIZED`. Test signals include probe/remove cycles, suspend/resume, firmware fallback, USB unplug during init, AP beaconing, calibration work start/stop, and TX/RX under queue teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/usb_mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/usb_mcu.c

Purpose: MT76x0 USB MCU firmware loader. It validates firmware headers, loads ILM/DLM segments over the shared mt76x02 USB firmware-data path, sends the IVB block with a vendor request, and marks the MCU running.

Important APIs/types/functions: `mt76x0u_mcu_init()`, `mt76x0u_load_firmware()`, `mt76x0u_upload_firmware()`, and `mt76x0_get_firmware()`. It consumes `struct mt76x02_fw_header`, `MT_MCU_IVB_SIZE`, `MT_MCU_DLM_OFFSET`, and `mt76x02u_mcu_fw_send_data()`.

Control flow: initialization enables USB DMA, returns early if firmware is already running, requests `mt7610e.bin` with fallback to `mt7610u.bin`, validates header size/ILM/DLM lengths, resets firmware, programs FCE/PSE registers, toggles UDMA drop, uploads ILM then DLM chunks, sends IVB via `MT_VEND_DEV_MODE`, and polls `MT_MCU_COM_REG0` for start.

State and persistence: only hardware/firmware state changes persist until device reset: FCE DMA pointers, USB DMA config, firmware running bit, and `MT76_STATE_MCU_RUNNING`. Firmware is requested from the kernel firmware loader but not modified.

Dependencies/integration: depends on Linux firmware APIs, mt76 USB vendor requests/bulk firmware transfer, mt76x02 MCU header layout, and mt76x0 firmware-running detection.

Risks: exact firmware size validation is critical; ILM length must exceed IVB size; bulk-transfer chunk limits and sleeps affect reliability; COM register polling controls failure detection. Test signals include missing `mt7610e.bin` fallback, malformed firmware lengths, firmware already running, COM timeout, and bulk or vendor-request failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x0/usb_mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02.h

Purpose: central shared state/API header for mt76x0/mt76x2-era devices. It defines `struct mt76x02_dev`, calibration state, beacon operations, rate-power storage, and exported common function prototypes used by USB and MMIO drivers.

Important APIs/types/functions: `struct mt76x02_dev`, `struct mt76x02_calibration`, `struct mt76x02_rx_freq_cal`, `struct mt76x02_beacon_ops`, `struct mt76x02_rate_power`, `struct beacon_bc_data`, chip predicates `is_mt76x0()`/`is_mt76x2()`, IRQ enable/disable helpers, and `mt76x02_wait_for_txrx_idle()`.

Control flow: this file is declarative; it connects call sites across TX/RX, station/interface management, beacon update, DMA, watchdog, debugfs, DFS, and PHY code by publishing prototypes. Inline helpers wrap register masks and chip ID decisions.

State and persistence: `mt76x02_dev` holds runtime state for TX status FIFO, calibration, watchdog counters, beacon timing, DFS detector, EDCCA, power limits, airtime, VIF MAC addresses, and work/timer objects. This state exists for the device lifetime and is not persistent across module unload/reset.

Dependencies/integration: includes core `mt76.h`, register/mac/dfs/dma headers, mac80211 types, kfifo, timers, workqueues, and mt76 phy/dev unions.

Risks: layout matters because the union with `mt76_dev`/`mt76_phy` must be first; many modules assume fields are initialized before use. Test signals are compile coverage for all bus variants, probe/start/stop cycles, watchdog reset, AP beacons, DFS region changes, EDCCA toggling, and station/key lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_beacon.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_beacon.c

Purpose: shared beacon SRAM and buffered broadcast/multicast handling for mt76x02 devices. It writes beacon frames into hardware memory, manages beacon masks, updates TBTT timer drift, and collects buffered PS frames.

Important APIs/types/functions: `mt76x02_init_beacon_config()`, `mt76x02_mac_set_beacon()`, `mt76x02_mac_set_beacon_enable()`, `mt76x02_resync_beacon_timer()`, `mt76x02_update_beacon_iter()`, and `mt76x02_enqueue_buffered_bc()`.

Control flow: init disables beacon/TBTT timers, enables sync mode, writes bypass mask, and programs slot offsets. Beacon update gathers active VIF beacons from mac80211, writes TXWI plus frame into each slot, updates `beacon_data_count`, and later releases bypass bits for populated slots. Enable/disable toggles per-VIF bits and starts/stops bus-specific beacon ops. Buffered BC frames are pulled per active VIF until a frame limit is reached, with only the tail frame clearing More Data.

State and persistence: uses device beacon mask, beacon interval, TBTT count, beacon hang counter, and per-update queued SKBs. Hardware beacon SRAM/register state persists until reset or reprogramming.

Dependencies/integration: called by MMIO pre-TBTT tasklet and USB hrtimer work, mac80211 beacon/buffered-BC APIs, mt76 CSA helpers, and `mt76x02_mac_write_txwi()`.

Risks: slot-size overflow, USB headroom assumptions, drift correction off by one, incorrect bypass masks, and More Data handling for buffered frames. Test signals include AP/multi-BSSID beacons, CSA completion, DTIM buffered multicast delivery, USB and PCI beacon paths, and small-slot ENOSPC warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_beacon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_debugfs.c

Purpose: debugfs surface for mt76x02 runtime diagnostics and EDCCA control. It exposes queue, AMPDU, DFS, power, rate-power, AGC, temperature, TPC, and watchdog counters.

Important APIs/types/functions: `mt76x02_init_debugfs()`, show helpers for AMPDU/DFS/rate power/AGC/txpower, and `fops_edcca` backed by `mt76_edcca_get()`/`mt76_edcca_set()`.

Control flow: initialization registers the common mt76 debugfs directory, then adds seqfiles and scalar debugfs entries. EDCCA writes take the mt76 mutex, update `ed_monitor_enabled`, enable actual monitoring only for ETSI DFS region, and reinitialize EDCCA hardware state.

State and persistence: debugfs reflects live kernel memory only. Mutable knobs are `enable_tpc` and `ed_monitor_enabled`; counters read calibration, DFS, aggregate, and watchdog state.

Dependencies/integration: depends on Linux debugfs/seq_file, mt76 debugfs registration, mt76 queue readers, mt76x02 DFS/EDCCA/calibration state, and device driver data on the dentry.

Risks: debugfs writes race with channel/regulatory transitions if locking is incomplete; EDCCA behavior is region-dependent; stats can be misleading after reset. Test signals include debugfs file creation, read stability during traffic, EDCCA toggling in ETSI vs non-ETSI regions, and watchdog reset counter visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dfs.c

Purpose: DFS radar detection implementation for MMIO mt76x02 devices. It configures region/bandwidth-specific hardware radar engines, collects hardware pulse reports and debug pulse events, runs a software pulse-sequence detector, and reports radar to mac80211.

Important APIs/types/functions: radar spec tables for ETSI/FCC/JP W53/W56, `mt76x02_dfs_init_detector()`, `mt76x02_dfs_init_params()`, `mt76x02_regd_notifier()`, `mt76x02_phy_dfs_adjust_agc()`, and the DFS tasklet.

Control flow: regulatory changes set the DFS domain under mutex, disable the tasklet, update EDCCA, program BBP DFS registers, enable GP timer interrupts, then re-enable. The tasklet skips scanning, periodically fetches event FIFO data into ring buffers, creates/extends PRI sequences, reports radar on sequence threshold, checks hardware engine status, validates pulse periods by region, and re-enables the GP timer IRQ.

State and persistence: `dev->dfs_pd` owns sequence lists, a pool, event ring buffers, stats, chirp counters, last timestamps, tasklet state, and software detector thresholds. Hardware DFS/IBI/AGC registers persist until channel/domain reset.

Dependencies/integration: mac80211 DFS state/`ieee80211_radar_detected()`, regulatory notifier, mt76 IRQ mask helpers, BBP register access, EDCCA initialization, and debugfs DFS stats.

Risks: false positives/negatives from region tables, timestamp wrap/reset, sequence pool accounting, tasklet/IRQ ordering, and scanning suppression. Test signals include region switch FCC/ETSI/JP, radar CAC channels, synthetic pulse patterns, debugfs stats increments, GP timer interrupt behavior, and no detection during scans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dfs.h

Purpose: data definitions for mt76x02 DFS detection. It describes radar specs, hardware/software detector events, sequence tracking, stats, thresholds, and public DFS entry points.

Important APIs/types/functions: `struct mt76x02_radar_specs`, `struct mt76x02_dfs_event`, `struct mt76x02_dfs_event_rb`, `struct mt76x02_dfs_sequence`, `struct mt76x02_dfs_pattern_detector`, constants such as `MT_DFS_EVENT_BUFLEN`, `MT_DFS_SEQUENCE_TH`, and public prototypes for init/regulatory/AGC adjustment.

Control flow: declarative header. Macros decode hardware event words and constants parameterize the detector implemented in `mt76x02_dfs.c`.

State and persistence: the pattern detector stores live radar sequence state and tasklet scheduling state. No data is persistent outside device lifetime.

Dependencies/integration: included by `mt76x02.h`; uses Linux list/tasklet types, nl80211 DFS regions through users, and BBP event formats.

Risks: constants define detection sensitivity and compliance behavior; ring size and sequence window changes can alter false-positive rates. Test signals include compile checks, DFS region conformance tests, event ring wrap, sequence pool growth/shrink, and debugfs stats matching detector activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dma.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dma.h

Purpose: shared DMA/FCE descriptor definitions for mt76x02. It defines TXD/RXFCE/MCU message bitfields, DMA ports, RX headroom/ring sizes, and DMA init/disable prototypes.

Important APIs/types/functions: `enum dma_msg_port`, `MT_TXD_INFO_*`, `MT_RX_FCE_INFO_*`, `MT_MCU_MSG_*`, `mt76x02_wait_for_wpdma()`, `mt76x02_dma_init()`, and `mt76x02_dma_disable()`.

Control flow: declarative header with one inline polling helper used before enabling/disabling MAC/DMA. TX/RX and MCU transports compose these fields when preparing descriptors or USB in-band command headers.

State and persistence: no local state. Constants affect persistent hardware queue/FCE register programming during runtime.

Dependencies/integration: includes `mt76x02.h` and core `dma.h`; consumed by MMIO DMA, USB TX preparation, and MCU response parsing.

Risks: bitfield mismatches corrupt transfer lengths, ports, encryption flags, or MCU sequence IDs. Test signals include TX/RX on all queues, MCU request/response sequence matching, USB DMA header padding, and DMA idle polling on reset/stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_dma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_eeprom.c

Purpose: shared EEPROM/eFUSE access helpers for mt76x02 devices. It reads 16-byte eFUSE blocks, copies EEPROM ranges, derives hardware band capabilities, checks external PA flags, and extracts RSSI/LNA calibration values.

Important APIs/types/functions: `mt76x02_get_efuse_data()`, `mt76x02_eeprom_copy()`, `mt76x02_eeprom_parse_hw_cap()`, `mt76x02_ext_pa_enabled()`, `mt76x02_get_rx_gain()`, and `mt76x02_get_lna_gain()`.

Control flow: eFUSE reads program address/mode/kick bits, poll for completion, treat all-ones AOUT as blank, and copy four data registers into the caller buffer. Capability parsing interprets board type from `NIC_CONF_0`. RX gain extraction reads shared LNA/RSSI offsets and falls back between 5 GHz groups if EEPROM fields are invalid.

State and persistence: reads from device eFUSE and `dev->mt76.eeprom.data`; it updates band capability flags in `mphy.cap` but does not persist changes externally.

Dependencies/integration: Linux unaligned helpers, mt76 register access, `mt76x02_eeprom.h`, mt76x2 and mt76x0 EEPROM loaders/PHY calibration.

Risks: byte/word offset errors, invalid field fallback, eFUSE timeout, and board capability misclassification. Test signals include blank eFUSE, valid EEPROM override, 2G-only/5G-only boards, external PA configurations, and RSSI calibration sanity across channel groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_eeprom.h

Purpose: shared mt76x02 EEPROM map and conversion helpers. It names offsets for chip ID, MAC, NIC configuration, RX gain, TX power, TSSI, temperature compensation, and usage-map fields.

Important APIs/types/functions: `enum mt76x02_eeprom_field`, `enum mt76x02_eeprom_modes`, `enum mt76x02_board_type`, `mt76x02_eeprom_get()`, `mt76x02_field_valid()`, sign-extension helpers, and `mt76x02_rate_power_val()`.

Control flow: declarative header; inline helpers validate odd/out-of-range offsets, decode little-endian words, and turn signed/optional EEPROM nibbles/bytes into calibrated signed values.

State and persistence: no mutable state. It defines the interpretation of persistent EEPROM/eFUSE bytes consumed by init and PHY power code.

Dependencies/integration: included by mt76x02 EEPROM helpers and mt76x2 EEPROM code; depends on unaligned access through callers and on `struct mt76x02_dev`.

Risks: offset aliases such as XTAL trim sharing addresses, signed-value polarity, optional enable-bit handling, and bounds checks returning `-1` as an int. Test signals include EEPROM fixture parsing, invalid/0xff fields, power table conversion, and channel/band capability derivation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mac.c

Purpose: shared MAC-layer logic for mt76x02. It handles WCID/key programming, TXWI construction, TX status reconstruction, RXWI parsing, MAC address/BSSID programming, protection/RTS settings, EDCCA monitoring, channel survey accounting, and periodic MAC work.

Important APIs/types/functions: `mt76x02_mac_write_txwi()`, `mt76x02_mac_process_rx()`, `mt76x02_send_tx_status()`, `mt76x02_mac_load_tx_status()`, WCID/key helpers, `mt76x02_mac_setaddr()`, `mt76x02_mac_set_tx_protection()`, `mt76x02_edcca_init()`, and `mt76x02_mac_work()`.

Control flow: TX builds rate/flags/power/PN/BA metadata into TXWI, then bus-specific code adds DMA transport. TX status is fetched from hardware FIFO, matched to skb pktids when possible, aggregated for no-skb AMPDU reports, converted into mac80211 rates/airtime, and submitted. RX strips padding/PN, fills decrypt/AMPDU/rate/RSSI/status fields, trims frame length, and hands packets to mt76. Periodic work updates survey/aggr counters, checks MAC errors, runs EDCCA, and reschedules.

State and persistence: programs key tables, WCID tables, BSSID registers, MAC address, protection registers, EDCCA block state, airtime counters, aggregation stats, and per-station cached TX status/packet length.

Dependencies/integration: mac80211, mt76 TX status/airtime/WCID helpers, tracepoints, EEPROM-derived calibration, register definitions, and USB/MMIO TX paths.

Risks: PN/key offload correctness, skb pktid lifecycle, AMPDU status coalescing, RX padding/PN stripping, rate conversion, EDCCA TX blocking, and MAC reset triggers. Test signals include encrypted traffic, AP/client multi-VIF, AMPDU retries, monitor/rate reporting, fragmented CCMP RX, airtime accounting, EDCCA busy-channel behavior, and beacon hang recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mac.h

Purpose: shared MAC data structure and bitfield header. It defines TX status, VIF/station private data, RXWI/TXWI layouts, RX info/rate flags, and MAC helper prototypes.

Important APIs/types/functions: `struct mt76x02_tx_status`, `struct mt76x02_vif`, `struct mt76x02_sta`, `struct mt76x02_rxwi`, `struct mt76x02_txwi`, `MT_VIF_WCID()`, packet-id masks, RXINFO/RXWI/TXWI bitfields, and `mt76x02_wait_for_mac()`.

Control flow: declarative header. `mt76x02_wait_for_mac()` polls MAC CSR0 until the device is responsive or removed/timeout.

State and persistence: station/VIF structs are embedded in mac80211 drv_priv and persist while interfaces/stations exist. TXWI/RXWI structs describe hardware descriptors passed per packet.

Dependencies/integration: used by shared MAC/TXRX, mt76x0/mt76x2 bus drivers, and reset paths. It depends on mac80211 SKB/status semantics and mt76 register access.

Risks: packed/aligned descriptor layout must match hardware; WCID mapping reserves group WCIDs near 254; rate bitfields affect both RX and TX status interpretation. Test signals include descriptor size/alignment checks, TX/RX on all PHY modes, multi-VIF group traffic, and MAC readiness timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mcu.c

Purpose: shared MCU message layer for MMIO mt76x02 devices. It sends command SKBs through the MCU TX queue, parses sequence-tagged responses, exposes common function/power/calibration commands, drains response queues, and formats firmware version strings.

Important APIs/types/functions: `mt76x02_mcu_msg_send()`, `mt76x02_mcu_parse_response()`, `mt76x02_mcu_function_select()`, `mt76x02_mcu_set_radio_state()`, `mt76x02_mcu_calibrate()`, `mt76x02_mcu_cleanup()`, and `mt76x02_set_ethtool_fwver()`.

Control flow: send allocates an MCU skb, takes the MCU mutex, assigns nonzero 4-bit sequence, writes FCE command info, queues to `q_mcu[MT_MCUQ_WM]`, then optionally drains responses until the matching sequence arrives or timeout. Calibration on MT76x2E clears and polls a COM register bit around the command.

State and persistence: updates `mcu.msg_seq`, `mcu_timeout`, response queue contents, firmware version in wiphy, and hardware radio/calibration state.

Dependencies/integration: mt76 MCU helpers, MMIO TX queues, mt76x02 DMA bitfields, firmware loaders, PCI watchdog restart, and mt76x2 channel/PHY calibration.

Risks: sequence wrap, stale responses, timeout poisoning through `mcu_timeout`, queue failure while mutex held, and calibration COM-bit polling. Test signals include command timeout/recovery, radio on/off, calibration commands, firmware restart, response sequence mismatch, and cleanup draining.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mcu.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mcu.h

Purpose: shared MCU constants, command enums, firmware headers, and common MCU API declarations for mt76x02 devices.

Important APIs/types/functions: `enum mcu_cmd`, `enum mcu_power_mode`, `enum mcu_function`, `struct mt76x02_fw_header`, `struct mt76x02_patch_header`, MCU register offsets, firmware memory offsets, and prototypes for cleanup/calibration/send/parse/function/radio/fwver helpers.

Control flow: declarative header. Bus-specific firmware loaders and common MCU send paths use these command IDs and binary header layouts.

State and persistence: no mutable state; defines interpretation of persistent firmware image headers and hardware MCU control registers.

Dependencies/integration: included by PCI/USB MCU loaders, mt76x0/mt76x2 init, and shared mt76x02 MCU code.

Risks: header layout is packed firmware ABI; command IDs must match firmware; wrong memory offsets brick firmware loading until reset. Test signals include firmware header validation, ROM patch loading, radio state commands, calibration commands, and ethtool firmware-version reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mmio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mmio.c

Purpose: MMIO/PCI DMA, interrupt, beacon tasklet, MAC start, and watchdog reset support for mt76x02 devices. This is the bus-specific counterpart to USB core support.

Important APIs/types/functions: `mt76x02_dma_init()`, `mt76x02_irq_handler()`, `mt76x02_rx_poll_complete()`, `mt76x02_dma_disable()`, `mt76x02_mac_start()`, `mt76x02_wdt_work()`, and `mt76x02_reconfig_complete()`.

Control flow: DMA init allocates TX status FIFO, attaches DMA ops, creates AC/PSD/MCU TX queues, RX queues, NAPI, TX worker, and pre-TBTT tasklet. IRQ handler acknowledges masked interrupts, disables serviced sources, schedules RX/TX NAPI, pre-TBTT beacon work, TBTT PSD kick, TX status polling, and DFS tasklet. Watchdog detects stuck TX DMA or MCU timeout, stops queues/NAPI/tasklets, optionally resets mac80211 state for MCU restart, resets DMA/MAC/queues, restarts MAC/MCU, and either asks mac80211 to restart or wakes queues.

State and persistence: hardware rings, irqmask, NAPI/worker/tasklet state, txstatus kfifo, DMA indices, reset/restart bits, beacon/DFS state, and queue contents.

Dependencies/integration: mt76 DMA core, mac80211 restart/queues, DFS, beacon common code, tracepoints, shared MCU cleanup/restart, and mt76x2 PCI init.

Risks: reset ordering across IRQ/NAPI/tasklets, WCID/key sync during restart, TX status FIFO overflow, DMA busy hangs, and beacon/DFS tasklet disable balance. Test signals include IRQ flood, TX hang watchdog, MCU timeout restart, suspend/resume, beacon AP mode, DFS timer interrupts, and queue cleanup under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_phy.c

Purpose: common PHY helper routines for mt76x02. It programs RX/TX chain paths, bandwidth/band registers, rate-power registers, VGA/AGC gain adjustment, and AGC gain initialization.

Important APIs/types/functions: `mt76x02_phy_set_rxpath()`, `mt76x02_phy_set_txdac()`, `mt76x02_phy_set_txpower()`, `mt76x02_phy_set_bw()`, `mt76x02_phy_set_band()`, `mt76x02_phy_adjust_vga_gain()`, `mt76x02_init_agc_gain()`, and rate-power min/max helpers.

Control flow: channel setup code derives rate power and calls these helpers to write ALC/TX power tables, band flags, bandwidth/control-channel fields, and antenna paths. Calibration periodically reads false CCA and adjusts AGC gain offset up/down within a low-gain-dependent limit.

State and persistence: writes BBP/TX power/band registers and updates `dev->cal.false_cca`, AGC gain arrays, low-gain flags, and gain-init marker.

Dependencies/integration: mt76x2 PCI/USB PHY paths, EEPROM-derived power tables, DFS AGC adjustment, EDCCA learning, and register definitions.

Risks: chainmask interpretation, signed power table packing, bandwidth/control channel mismatch, and unstable AGC adjustment from noisy false-CCA counters. Test signals include 1x1/2x2 antenna modes, 20/40/80 MHz channels, TX power limit changes, false-CCA stress, and channel switch calibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_phy.h

Purpose: common PHY helper declarations and inline gain/rate index helpers for mt76x02.

Important APIs/types/functions: inline `mt76x02_get_l_gain()`/`mt76x02_get_h_gain()`, and prototypes for rate-power offset/limit/max, TX power, RX path, TX DAC, bandwidth/band, VGA gain, and AGC initialization.

Control flow: declarative header; channel and calibration code include it to share helper contracts.

State and persistence: no local state. Helpers read calibration arrays and write hardware through implementations in `mt76x02_phy.c`.

Dependencies/integration: included by mt76x2 init/PHY and shared PHY code; depends on `struct mt76x02_dev` and rate-power struct from `mt76x02.h`.

Risks: inline gain indexing must match chain number; callers must initialize AGC gains before reading them. Test signals include compile coverage, channel switch after AGC init, single-chain and dual-chain gain reads, and TX power register programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_regs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_regs.h

Purpose: register map and bitfield definitions for mt76x02 hardware. It names MAC, DMA, USB, MCU, BBP, RF, beacon, WCID, protection, TX power, EDCCA, DFS, and timing registers used throughout the driver.

Important APIs/types/functions: register-address macros such as `MT_WPDMA_GLO_CFG`, `MT_USB_DMA_CFG`, `MT_BCN_OFFSET()`, `MT_WCID_*`, `MT_BBP()`, and numerous `GENMASK`/`BIT` field definitions for register composition.

Control flow: declarative header. All runtime control flow in MAC/PHY/DMA/MCU code relies on these constants to read/modify/write hardware.

State and persistence: no local state; it defines the address/bit layout of persistent device registers.

Dependencies/integration: included by `mt76x02.h` and all shared/bus-specific mt76x02 modules; assumes mt76 register accessors and Linux bitfield macros.

Risks: a wrong address or mask can affect unrelated hardware functions; overlapping fields require careful `mt76_rmw_field()` use. Test signals include broad compile coverage, probe/init register programming, TX/RX, beacons, DFS, EEPROM/eFUSE reads, and hardware reset paths across revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_trace.c

Purpose: tracepoint instantiation unit for mt76x02. It defines `CREATE_TRACE_POINTS` and includes the mt76x02 trace header so the trace events have exactly one definition.

Important APIs/types/functions: `CREATE_TRACE_POINTS` and inclusion of `mt76x02_trace.h`.

Control flow: no runtime control flow beyond generated tracepoint code. Other modules call trace events declared in the header.

State and persistence: tracepoint registration is kernel instrumentation state; no driver data is persisted here.

Dependencies/integration: Linux tracepoint infrastructure and `mt76x02_trace.h`.

Risks: duplicate or missing instantiation breaks builds or disables trace events. Test signals include kernel build with tracing, enabling mt76x02 trace events, and observing TX status poll/fetch records during traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_trace.h

Purpose: trace event declarations for mt76x02-specific diagnostics, primarily TX status polling/fetching.

Important APIs/types/functions: `TRACE_SYSTEM mt76x02`, `DECLARE_EVENT_CLASS(dev_evt)`, `DEFINE_EVENT(mac_txstat_poll)`, and `TRACE_EVENT(mac_txstat_fetch)` with WCID, pktid, rate, retry, ack, success, aggregation, and validity fields.

Control flow: trace macros generate static tracepoints used by `mt76x02_mac_poll_tx_status()` and `mt76x02_mac_load_tx_status()`.

State and persistence: trace events capture transient runtime state into the kernel tracing buffers when enabled; no device state is changed.

Dependencies/integration: Linux tracepoint API, `mt76x02_tx_status`, and include path/file macros for trace generation.

Risks: field layout must match the status struct; tracing must remain low-overhead when disabled. Test signals include building with tracepoints, enabling `mt76x02:*`, and validating txstat fetch/poll events against TX status debug behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_txrx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_txrx.c

Purpose: shared TX/RX glue between mac80211/mt76 core and mt76x02 MAC descriptors. It chooses WCIDs for outgoing frames, dispatches MCU vs data RX, computes TX power adjustment, exposes TX status polling, and prepares MMIO TXWI metadata.

Important APIs/types/functions: `mt76x02_tx()`, `mt76x02_queue_rx_skb()`, `mt76x02_tx_get_max_txpwr_adj()`, `mt76x02_tx_get_txpwr_adj()`, `mt76x02_tx_set_txpwr_auto()`, `mt76x02_tx_status_data()`, and `mt76x02_tx_prepare_skb()`.

Control flow: TX selects station WCID, VIF group WCID, or global WCID, then calls mt76 core TX. RX sends MCU queue packets to `mt76_mcu_rx_event()` and data packets through RXWI parsing before mt76 RX. MMIO TX preparation writes TXWI, allocates pktid, encodes fallback rate in no-skb pktids, selects EDCA/MGMT qsel, sets WIV, and updates per-station packet length EWMA.

State and persistence: updates packet-id maps, station EWMA length, WCID drop state for PSD queue, TXWI contents, auto-protection TX power fields, and rate-power-derived adjustment.

Dependencies/integration: shared MAC code, mt76 TX/RX core, mac80211 rate flags, DMA bitfields, and USB/MMIO driver ops.

Risks: wrong WCID selection, pktid leak on errors, TX power adjustment encoding, and MCU RX queue misclassification. Test signals include station/group/global traffic, AMPDU with no skb status, encrypted WIV handling, MCU events, and TX power changes with TPC enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb.h

Purpose: public prototypes for the mt76x02 USB support layer. It exposes USB MAC start, MCU init/firmware reset/data upload, TX DMA-info preparation/completion, and USB beacon timer setup/teardown.

Important APIs/types/functions: `mt76x02u_mac_start()`, `mt76x02u_init_mcu()`, `mt76x02u_mcu_fw_reset()`, `mt76x02u_mcu_fw_send_data()`, `mt76x02u_skb_dma_info()`, `mt76x02u_tx_prepare_skb()`, `mt76x02u_tx_complete_skb()`, `mt76x02u_init_beacon_config()`, and `mt76x02u_exit_beacon_config()`.

Control flow: declarative header linking mt76x0/mt76x2 USB bus drivers to shared USB core/MCU helpers.

State and persistence: no local state; callers affect USB DMA headers, firmware upload state, and beacon timers.

Dependencies/integration: includes `mt76x02.h`; consumed by mt76x0 USB, mt76x2 USB, and mt76x02 USB implementation files.

Risks: prototypes must stay aligned with shared USB implementations and driver ops. Test signals include build coverage for `CONFIG_MT76x02_USB`, USB firmware loading, TX completion, and AP beacons on USB devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb_core.c

Purpose: shared mt76x02 USB core for TX preparation/completion, MAC start, and software pre-TBTT beacon timing. It adapts common txwi/beacon code to USB bulk transport.

Important APIs/types/functions: `mt76x02u_mac_start()`, `mt76x02u_skb_dma_info()`, `mt76x02u_tx_prepare_skb()`, `mt76x02u_tx_complete_skb()`, `mt76x02u_init_beacon_config()`, `mt76x02u_exit_beacon_config()`, and pre-TBTT hrtimer/work helpers.

Control flow: TX prep inserts header padding, writes txwi in skb headroom, assigns pktid, chooses qsel, adds DMA info/padding, and releases pktid on failure. Completion removes DMA/txwi/pad before mt76 status completion. MAC start enables TX then RX after WPDMA idle polling. Beacon config uses an hrtimer to run work about 8 ms before TBTT, writes beacons and buffered BC frames into limited beacon SRAM, updates CSA, then re-arms based on TSF/TBTT.

State and persistence: skb layout, pktid maps, station EWMA length, USB beacon hrtimer/work, beacon slot count, and MAC/RX filter registers.

Dependencies/integration: mt76 USB bulk queues, common MAC/beacon/TXRX helpers, hrtimer/workqueues, mac80211 beacon APIs, and DMA bitfields.

Risks: skb headroom/padding corruption, pktid cleanup on pad failure, beacon timer rearm races, USB limited beacon slots, and TBTT drift. Test signals include TX completion status, AMSDU/SG headroom, AP beacons with buffered multicast, CSA, stop/remove while timer active, and MAC start timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb_mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb_mcu.c

Purpose: shared mt76x02 USB MCU transport and firmware-upload helper. It implements in-band USB command messages, random register read/write batches, response polling, firmware reset, and chunked firmware transfer through FCE.

Important APIs/types/functions: `mt76x02u_init_mcu()`, `mt76x02u_mcu_fw_reset()`, `mt76x02u_mcu_fw_send_data()`, USB MCU send/read/write helpers, and `mt76x02u_mcu_wait_resp()`.

Control flow: normal MCU send allocates an skb, locks the MCU mutex, optionally assigns a sequence, prepends USB DMA info, bulk-sends to the in-band command endpoint, and waits on command-response endpoint for matching done event. Random writes recurse over max packet-sized chunks; random reads require one command and place returned values into caller pairs. Firmware upload writes FCE DMA address/length, bulk-sends a command header plus payload, bumps CPU descriptor index, and sleeps between chunks.

State and persistence: uses `usb->mcu.data`, `rp/rp_len/base`, `mcu.msg_seq`, and hardware FCE/descriptor registers. Firmware data changes MCU memory until reset.

Dependencies/integration: mt76 USB bulk/vendor helpers, shared MCU parse response, DMA/FCE bitfields, mt76x0/mt76x2 USB firmware loaders.

Risks: response sequence mismatch, read-pair length mismatch, recursive write depth, fixed response retries, firmware chunk alignment, and removed-device behavior. Test signals include random register read/write, command timeout, firmware chunk upload, unplug during MCU command, and multi-command sequence wrap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb_mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_util.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_util.c

Purpose: shared mt76x02 mac80211 utility layer. It initializes hw capabilities, interface combinations, LEDs, filters, station/VIF lifecycle, aggregation, keys, EDCA, coverage/RTS, scanning completion, PS handling, BSS changes, and address lists.

Important APIs/types/functions: `mt76x02_init_device()`, `mt76x02_configure_filter()`, `mt76x02_sta_add/remove()`, `mt76x02_add/remove_interface()`, `mt76x02_ampdu_action()`, `mt76x02_set_key()`, `mt76x02_conf_tx()`, `mt76x02_set_coverage_class()`, `mt76x02_bss_info_changed()`, and `mt76x02_config_mac_addr_list()`.

Control flow: init configures queues, rate limits, interface combinations, LED callbacks, DFS notifier for MMIO, drv_priv sizes, chain masks, antenna masks, and hardware flags. Interface add assigns BSSID indexes with STA offset handling. Key setup rejects unsupported ciphers/topologies, maps keys to WCIDs/shared key tables, and requests software fallback when needed. BSS changes program BSSID/protection/beacon interval/enable/preamble/slot time.

State and persistence: updates wiphy/mac80211 capability state, vif/wcid masks, WCID table, hardware key tables, RX filter, EDCA/protection registers, slottime/coverage, scan/calibration state, LED config, and MAC address list.

Dependencies/integration: mac80211 callbacks, mt76 core WCID/TXQ/key helpers, shared MAC/DFS/beacon code, LEDs, and USB/MMIO feature differences.

Risks: multi-VIF index conflicts, key-offload fallback correctness, USB AP GTK limitation, AMPDU state transitions, and filter flag inversion. Test signals include AP/STA/P2P/mesh combinations, WEP/TKIP/CCMP, AMPDU start/stop, EDCA changes, scanning recovery, TIM/beacon changes, and SAR/antenna capability reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/Kconfig

Purpose: Kconfig entries for mt76x2 common, PCIe, and USB drivers.

Important APIs/types/functions: symbols `MT76x2_COMMON`, `MT76x2E`, and `MT76x2U`. PCIe depends on `MAC80211` and `PCI`; USB depends on `MAC80211` and `USB` and selects `MT76x02_USB`; both select common code.

Control flow: build-time configuration only. Selecting a bus-specific symbol pulls in the shared mt76x2 and mt76x02 support modules needed by that transport.

State and persistence: no runtime state. It controls kernel configuration/module availability.

Dependencies/integration: Linux Kconfig, mt76 parent Kconfig, mac80211, PCI, USB, and the Makefile object split.

Risks: missing selects cause unresolved symbols; overly broad dependencies expose unsupported builds. Test signals include `allyesconfig`, modular builds for PCI and USB separately, and verifying help text/device coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/Makefile

Purpose: Makefile object composition for mt76x2 drivers.

Important APIs/types/functions: builds `mt76x2-common.o`, `mt76x2e.o`, and `mt76x2u.o`. Common objects are EEPROM, MAC, init, PHY, and MCU; PCIe adds probe/main/init/MCU/PHY; USB adds USB probe/init/main/MAC/MCU/PHY.

Control flow: build-system declarative file; Kconfig symbols decide which composite objects are linked.

State and persistence: no runtime state.

Dependencies/integration: Linux kbuild, `CONFIG_MT76x2_COMMON`, `CONFIG_MT76x2E`, and `CONFIG_MT76x2U`; mirrors header/API boundaries in source.

Risks: object omissions cause link failures or missing module init; wrong split can pull USB-only code into PCI builds or vice versa. Test signals include PCI-only, USB-only, and both-enabled module builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/eeprom.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/eeprom.c

Purpose: MT76x2 EEPROM/eFUSE parser and power calibration source. It loads EEPROM/OTP, optionally merges calibration-free OTP data, validates chip IDs, reads MAC address, derives RX gain, rate-power tables, per-channel power info, and temperature compensation data.

Important APIs/types/functions: `mt76x2_eeprom_init()`, `mt76x2_read_rx_gain()`, `mt76x2_get_rate_power()`, `mt76x2_get_power_info()`, `mt76x2_get_temp_comp()`, and calibration-free helpers.

Control flow: EEPROM load initializes a 512-byte EEPROM buffer, checks EEPROM chip ID if found, allocates OTP, reads eFUSE, merges selected OTP bytes when DT property `mediatek,eeprom-merge-otp` and cal-free pattern match, or falls back to eFUSE. Init parses hardware capabilities, reads/overrides MAC, and clears local-admin-derived bit. Power helpers map channels into 5 GHz groups, select delta indexes, decode signed optional fields, and compute target/TSSI/temp data.

State and persistence: fills `dev->mt76.eeprom`, `dev->mt76.otp`, `mphy.macaddr`, band caps, and calibration RX fields. It reads persistent EEPROM/eFUSE but writes only runtime copies.

Dependencies/integration: mt76 EEPROM core, OF properties, shared mt76x02 EEPROM helpers, mt76x2 PHY/channel setup, and regulatory power initialization.

Risks: incomplete eFUSE accepted by FIXME path, DT merge policy, group/delta indexing, invalid field fallbacks, and MAC override behavior. Test signals include valid EEPROM, OTP-only boards, cal-free merge, invalid chip IDs, MAC override, 2G/5G power tables, and temp/TSSI enable bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/eeprom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/eeprom.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/eeprom.h

Purpose: MT76x2-specific EEPROM type declarations and capability predicates.

Important APIs/types/functions: `enum mt76x2_cal_channel_group`, `struct mt76x2_tx_power_info`, `struct mt76x2_temp_comp`, prototypes for power/RX/temp helpers, and inline predicates `mt76x2_has_ext_lna()`, `mt76x2_temp_tx_alc_enabled()`, and `mt76x2_tssi_enabled()`.

Control flow: declarative header; PHY and init code call these helpers to decide power-control and gain paths.

State and persistence: no local state; structs carry decoded runtime views of EEPROM/eFUSE calibration.

Dependencies/integration: includes shared `mt76x02_eeprom.h`; used by mt76x2 EEPROM, init, MCU, and PHY code.

Risks: predicates encode mutually exclusive temp ALC vs TSSI behavior; wrong NIC_CONF bit interpretation changes calibration mode. Test signals include EEPROM bit combinations for external LNA, temp ALC, and TSSI; channel group coverage; and compile checks for all mt76x2 objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/init.c

Purpose: MT76x2 common initialization helpers. It handles SAR power updates, WLAN reset/power state, default MAC register programming, and per-channel max power initialization.

Important APIs/types/functions: `mt76x2_set_sar_specs()`, `mt76x2_reset_wlan()`, `mt76_write_mac_initvals()`, and `mt76x2_init_txpower()`.

Control flow: SAR update validates chandef, initializes SAR data, converts configured power to per-chain units on 2x2 devices, and reprograms TX power if running. WLAN reset toggles function clock/reset bits. MAC init writes a large reference register table plus default protection configs. TX power init iterates each supported channel, reads EEPROM target/rate power, computes `orig_mpwr`, converts to combined 2x2 output, and clamps to regulatory max.

State and persistence: updates `txpower_conf`, SAR state, WLAN control registers, MAC/protection/TX power defaults, and channel `orig_mpwr`/`max_power` fields.

Dependencies/integration: cfg80211 SAR helpers, mt76 register pair writes, shared EEPROM/power helpers, mt76x2 PHY TX power, and channel registration.

Risks: per-chain vs combined power conversion, invalid chandef path, reference register magic values, and regulatory max interaction. Test signals include SAR updates while running/stopped, channel power listings, 2G/5G band registration, WLAN reset after suspend, and TX power debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mac.c

Purpose: MT76x2 MAC stop helper. It disables EDCCA/TX hold behavior, stops MAC TX/RX, waits for idle, and optionally forces BBP core resets when idle does not arrive.

Important APIs/types/functions: `mt76x2_mac_stop()` and exported symbol; local state includes saved RTS retry config.

Control flow: clear EDCCA/TX40M hold bits, write `MT_MAC_SYS_CTRL` to zero, mask RTS retry limit, poll MAC status and IBI busy for up to 300 us, optionally pulse BBP core reset bits if forced and still busy, then restore RTS config.

State and persistence: changes MAC system control, TXOP/holder bits, RTS config temporarily, and possible BBP reset state.

Dependencies/integration: used by PCI start/stop/channel/reset, common PHY calibration, and watchdog paths. Resume is declared inline in `mac.h`.

Risks: forced reset during active traffic, insufficient idle polling, and restoring RTS config after failure. Test signals include channel switching, interface stop, watchdog reset, forced stop during TX/RX load, and EDCCA re-enable after restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mac.h

Purpose: MT76x2 MAC helper declarations. It exposes MAC stop and an inline resume helper that re-enables MAC TX/RX.

Important APIs/types/functions: `mt76x2_mac_stop()` and `mt76x2_mac_resume()`.

Control flow: declarative header with one inline register write for resume. Channel switch and reset paths stop MAC, adjust PHY/channel, then resume.

State and persistence: resume writes `MT_MAC_SYS_CTRL_ENABLE_TX|RX`; stop implementation manipulates MAC/BBP state.

Dependencies/integration: included by `mt76x2.h` and PCI/PHY code; depends on shared register definitions through mt76x2 includes.

Risks: callers must pair stop/resume under appropriate locks/tasklet disable; resume without reinitializing RX filter/DMA can expose stale state. Test signals include channel switch, calibration stop/resume, and watchdog recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mcu.c

Purpose: MT76x2 common MCU command helpers for channel switching, CR loading, gain initialization, and TSSI compensation.

Important APIs/types/functions: `mt76x2_mcu_set_channel()`, `mt76x2_mcu_load_cr()`, `mt76x2_mcu_init_gain()`, and `mt76x2_mcu_tssi_comp()`.

Control flow: channel switch sends `CMD_SWITCH_CHANNEL_OP` twice: first without extension channel, then after a short delay with `0xe0 + bw_index`. CR load sends NIC configuration-derived mode data. Gain init can set a force bit in the channel word. TSSI compensation wraps calibration data in `CMD_CALIBRATION_OP`.

State and persistence: updates firmware/MCU channel, BBP/RF CR state, gain tables, and TSSI calibration state.

Dependencies/integration: shared mt76 MCU send path, mt76x2 EEPROM config bits, mt76x2 PCI/USB PHY channel setup and calibration.

Risks: two-step channel switch ordering, bandwidth index encoding, EEPROM config packing, and calibration command timeout. Test signals include 20/40/80 MHz channel switches, scans vs normal channel changes, forced gain init, TSSI-enabled devices, and MCU timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mcu.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mcu.h

Purpose: MT76x2-specific MCU register offsets, calibration IDs, CR modes, TSSI compensation struct, and helper prototypes.

Important APIs/types/functions: MCU memory/remap offsets, `enum mcu_calibration`, `enum mt76x2_mcu_cr_mode`, `struct mt76x2_tssi_comp`, `mt76x2_mcu_tssi_comp()`, and `mt76x2_mcu_init_gain()`.

Control flow: declarative header used by PCI/USB firmware loaders and PHY calibration code to choose commands and memory offsets.

State and persistence: no mutable state; constants define firmware memory ABI and calibration command IDs.

Dependencies/integration: includes shared `mt76x02_mcu.h`; consumed by mt76x2 MCU, PCI MCU, USB MCU, and PHY.

Risks: offsets differ by revision; wrong calibration IDs cause firmware-side miscalibration. Test signals include ROM patch/firmware loading on E2/E3+, channel calibration commands, and TSSI compensation commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mt76x2.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mt76x2.h

Purpose: top-level MT76x2 common header. It defines firmware names/EEPROM size, chip predicates, DFS silent-channel helper, public mac80211 ops, and cross-module prototypes for registration, init, EEPROM, PHY, MCU, MAC, and cleanup.

Important APIs/types/functions: `MT7662_FIRMWARE`, `MT7662_ROM_PATCH`, `is_mt7612()`, `mt76x2_channel_silent()`, `mt76x2_ops`, and prototypes for PCI/USB channel, PHY, MCU, reset, TX power, and gain helpers.

Control flow: declarative integration point; bus-specific drivers include it to share the mt76x2 common object API.

State and persistence: no local state. `mt76x2_channel_silent()` reads current channel DFS state to suppress calibration on unavailable radar channels.

Dependencies/integration: Linux device/network headers, shared `mt76x02.h`, and mt76x2 `mac.h`.

Risks: common prototypes must match object split; silent-channel logic affects regulatory DFS behavior. Test signals include PCI/USB builds, firmware request names, DFS unavailable channels, and channel calibration suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mt76x2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mt76x2u.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mt76x2u.h

Purpose: MT76x2 USB-specific public header. It declares USB driver operations, firmware/init/cleanup helpers, USB MAC/PHY/MCU functions, queue management, and USB aggregation constants.

Important APIs/types/functions: `MT7612U_EEPROM_SIZE`, `MT_USB_AGGR_SIZE_LIMIT`, `MT_USB_AGGR_TIMEOUT`, `mt76x2u_ops`, register/init/cleanup/stop, USB MAC reset/stop, USB PHY channel/calibration, USB MCU init/firmware init, and queue helpers.

Control flow: declarative header used by USB-only mt76x2 source files listed in the Makefile.

State and persistence: no local state; constants drive USB DMA aggregation and EEPROM sizing in implementation files.

Dependencies/integration: includes common `mt76x2.h` and `mcu.h`; consumed by mt76x2 USB probe/init/main/MAC/MCU/PHY objects.

Risks: prototypes bridge transport-specific code not present in PCI builds; aggregation constants affect throughput/latency. Test signals include USB-only build, probe/register, firmware load, queue allocation/deinit, channel setting, and USB aggregation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/mt76x2u.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci.c

Purpose: PCIe bus driver entry point for MT7612/MT7602/MT7662. It matches PCI IDs, enables the device, maps BARs, configures DMA/IRQ, allocates mt76 device state, registers mt76x2 common device, handles remove, and implements PCI suspend/resume.

Important APIs/types/functions: `mt76x2e_probe()`, `mt76x2e_remove()`, suspend/resume callbacks, `mt76x2e_device_table`, `mt76pci_driver`, and PCI-specific `mt76_driver_ops`.

Control flow: probe enables PCI, maps BAR0, sets bus master and 32-bit DMA mask, allocates `mt76x02_dev`, initializes MMIO, powers WLAN off, reads ASIC revision, masks IRQs, requests shared IRQ using `mt76x02_irq_handler()`, registers the device, applies ASPM fixups, and disables ASPM. Suspend disables NAPI/tasklets/worker and saves PCI power state; resume restores power/state, re-enables processing, schedules NAPI, and resumes hardware.

State and persistence: PCI drvdata, mapped MMIO, IRQ registration, DMA mask, mt76 device state, PCI power state, and ASPM-related registers.

Dependencies/integration: Linux PCI PM APIs, mt76 MMIO, shared mt76x02 IRQ/DMA/TXRX, mt76x2 registration/resume/cleanup.

Risks: probe error cleanup before drvdata/registration, suspend tasklet kill vs later resume, IRQ sharing, DMA mask limits, and ASPM magic register writes. Test signals include PCI probe/remove, module unload, suspend/resume, IRQ traffic, ASPM platforms, and unsupported DMA mask failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_init.c

Purpose: MT76x2 PCI/MMIO hardware initialization, reset, power-on, resume, stop, cleanup, and device registration.

Important APIs/types/functions: `mt76x2_mac_reset()`, `mt76x2_resume_device()`, `mt76x2_stop_hardware()`, `mt76x2_cleanup()`, `mt76x2_register_device()`, plus PBF/RF power/XTAL helpers.

Control flow: init disables DMA, enables WLAN, powers RF, loads EEPROM, resets MAC/hardware tables, saves RX filter, initializes DMA, marks initialized, starts MAC, initializes MCU firmware, then stops MAC until mac80211 start. MAC reset waits for MAC, configures WPDMA/PBF/default registers/XTAL/RF bypass/MCU clock, programs MAC address and beacon config, and on hard reset clears WCID/drop/key/status tables. Register initializes calibration work, common device caps, hardware, address list, mac80211 registration, debugfs, and channel power.

State and persistence: hardware power/RF/MAC/PBF/WCID/key/register state, DMA queues, initialized/running bits, calibration/watchdog/mac work, firmware state, and debugfs/mac80211 registration.

Dependencies/integration: mt76x2 EEPROM/MCU/MAC/PHY, shared mt76x02 DMA/MAC/beacon/debugfs, mt76 registration, Linux delay APIs.

Risks: hardware reset ordering, hard vs soft reset table clearing, RF power magic values, firmware initialization after MAC start, and failure cleanup after mac80211 registration. Test signals include cold probe, resume, channel start, module unload, MAC reset timeout, EEPROM failure, DMA init failure, and debugfs/channel-power availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_main.c

Purpose: MT76x2 PCI mac80211 operations and channel/config control. It starts/stops the radio, applies channel changes, handles monitor/power changes, antenna selection, and publishes `mt76x2_ops`.

Important APIs/types/functions: `mt76x2_start()`, `mt76x2_stop()`, `mt76x2e_set_channel()`, `mt76x2_config()`, `mt76x2_set_antenna()`, and `mt76x2_ops`.

Control flow: start enables MAC, starts PHY/radio, schedules MAC/watchdog work, and sets running. Stop clears running and stops hardware. Channel switch disables beacon/DFS tasklets, force-stops MAC, programs PHY channel, resets survey counters and DFS params, resumes MAC, then re-enables tasklets. Config updates RX filter for monitor mode and recalculates SAR-adjusted per-chain TX power on power changes. Antenna updates chainmask/antenna mask and programs PHY.

State and persistence: running bit, RX filter, txpower_conf, chainmask/antenna mask, tasklet enable state, channel definition, survey counters, DFS params, and delayed work.

Dependencies/integration: mac80211 ops, shared mt76x02 utility callbacks, mt76x2 PHY/MAC/hardware stop, mt76 SAR helpers, DFS/beacon tasklets.

Risks: monitor flag inversion, channel switch while tasklets active, power conversion for 2x2, empty flush implementation, and antenna invalid combinations. Test signals include start/stop, channel switch with AP beaconing, monitor mode toggles, txpower/SAR changes, antenna 1/2/3 settings, and DFS channel entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_mcu.c

Purpose: MT76x2 PCI firmware loader and MCU initialization/restart path. It loads the ROM patch and main firmware over MMIO remap windows, configures MCU ops, and supports watchdog-triggered MCU restart.

Important APIs/types/functions: `mt76x2_mcu_init()`, `mt76pci_load_rom_patch()`, `mt76pci_load_firmware()`, and `mt76pci_mcu_restart()`.

Control flow: ROM patch optionally takes hardware semaphore, checks revision-specific already-applied bit, requests `mt7662_rom_patch.bin`, remaps PCIE base, copies patch to MCU memory, triggers ROM, polls completion, releases semaphore. Firmware requests `mt7662.bin`, validates ILM/DLM size, logs version/build, copies ILM and DLM to revision-specific addresses, handles XTAL option bit, triggers firmware, polls start, and sets wiphy firmware version. MCU init installs send/parse/restart ops, loads patch/firmware, and selects queue. Restart cleans MCU, hard-resets MAC, reloads firmware, and resets WPDMA indices.

State and persistence: MCU firmware memory, COM/CLOCK/semaphore registers, remap base, firmware version string, MCU ops, and WPDMA reset state.

Dependencies/integration: Linux firmware API, shared mt76x02 MCU send/parse/cleanup, mt76x2 MAC reset, EEPROM XTAL option, watchdog reset.

Risks: semaphore timeout/leak, revision-specific patch bit/address, firmware size validation, DLM address differences, and restart failure after queues are reset. Test signals include missing/invalid firmware, already-applied ROM patch, E2 vs E3+ hardware, MCU timeout watchdog restart, and ethtool firmware-version output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_phy.c

Purpose: MT76x2 PCI PHY channel setup and periodic calibration. It handles TSSI initialization, per-channel calibrations, antenna programming, channel/bandwidth programming, RX gain/power setup, temperature/TSSI compensation, and radio start.

Important APIs/types/functions: `mt76x2_phy_set_channel()`, `mt76x2_phy_set_antenna()`, `mt76x2_phy_calibrate()`, `mt76x2_phy_start()`, and internal TSSI/channel/temp compensation helpers.

Control flow: channel setup computes bandwidth and extension-channel indexes for 20/40/80 MHz, reads RX gain, programs TX power registers/delay/power, sets band/bandwidth/ext CCA, sends MCU channel and gain commands, programs antenna and LDPC, runs initial RC/RXDCOC and channel calibrations when not scanning, initializes AGC, sets default temp compensation, and schedules calibration work. Periodic calibration runs channel calibration if pending, TSSI/temp compensation, channel gain update, then reschedules. Radio start sends radio-on and loads CRs.

State and persistence: calibration flags, TSSI/temp/agc/rx gain state, channel definition, BBP/RF/TX power registers, antenna chain state, EDCCA state, and delayed calibration work.

Dependencies/integration: mt76x2 EEPROM/MCU/MAC/common PHY helpers, mac80211 DFS channel state, mt76 register access, EDCCA, and workqueues.

Risks: calibration must be skipped on silent DFS channels, scan path avoids disruptive calibration, bandwidth index math, external PA/TSSI/temp ALC interactions, and antenna register consistency. Test signals include 20/40/80 MHz channels, DFS unavailable channels, scan channel changes, TSSI/temp-enabled EEPROMs, single/dual antenna modes, and calibration work under traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/pci_phy.c -->
