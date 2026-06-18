# subset-b-004917 research

This grouped report covers the exact source files assigned to `subset-b-004917`. Each section preserves the source path in its title and is wrapped with reconciliation markers for deterministic splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c_table.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c_table.h

Purpose: declares the externally defined Realtek RTL8822C initialization and calibration tables used by the rtw88 chip description. The file does not own data; it is the typed link between `rtw8822c.c` and the generated/static table providers in the same driver family.

Important APIs/types: all symbols are `extern const struct rtw_table`: MAC, AGC, BB, BB power-by-rate, RF path A/B, two TX power limit variants, DPK AFE/non-DPK, DPK MAC/BB, and MP calibration initialization tables. These depend on `struct rtw_table` from the rtw88 table-loader infrastructure.

Control flow and state: no runtime control flow or persistent state exists here. The declarations are consumed during chip bring-up when common code calls `rtw_load_table()` through fields in the chip info structure.

Dependencies and integration: depends on the rtw88 chip-table model and the corresponding compiled table objects. Any declaration/name drift breaks link-time integration or chip initialization.

Risks and test signals: table names are hardware contract points, so the main risks are missing object files, wrong table assignment in chip info, or ABI drift in `struct rtw_table`. Build/link tests and successful RTL8822C power-on/table load logs are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822c_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822ce.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822ce.c

Purpose: PCI module glue for RTL8822CE-class devices. It binds Realtek PCI IDs `0xC822` and `0xC82F` to the shared `rtw8822c_hw_spec` and delegates all behavior to the rtw88 PCI HCI layer.

Important APIs/types: `rtw_8822ce_id_table`, `struct pci_driver rtw_8822ce_driver`, `MODULE_DEVICE_TABLE(pci, ...)`, and `module_pci_driver()`. The driver uses `rtw_pci_probe`, `rtw_pci_remove`, `rtw_pci_shutdown`, `rtw_pci_err_handler`, and `rtw_pm_ops`.

Control flow and state: kernel PCI matching calls `rtw_pci_probe()` with `driver_data` pointing to the 8822C hardware spec. Removal, shutdown, runtime/system power management, and PCI error recovery are entirely handled by the shared PCI module.

Dependencies and integration: depends on `pci.h`, `rtw8822c.h`, Linux PCI core, and the common rtw88 PCI transport. It integrates with mac80211 only after the shared probe path allocates and registers the hardware.

Risks and test signals: risk is limited to PCI ID coverage and wrong hardware-spec pointer assignment. Test by building the module, checking `modinfo` aliases, probing matching hardware, exercising suspend/resume and PCI AER recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822ce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822cs.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822cs.c

Purpose: SDIO module glue for RTL8822CS. It registers a Linux `sdio_driver` for `SDIO_DEVICE_ID_REALTEK_RTW8822CS` and passes `rtw8822c_hw_spec` to the shared rtw88 SDIO HCI implementation.

Important APIs/types: `rtw_8822cs_id_table`, `MODULE_DEVICE_TABLE(sdio, ...)`, `struct sdio_driver rtw_8822cs_driver`, `module_sdio_driver()`, and the shared entry points `rtw_sdio_probe`, `rtw_sdio_remove`, `rtw_sdio_shutdown`, `rtw_sdio_pm_ops`.

Control flow and state: the MMC/SDIO core matches the vendor/device ID and calls `rtw_sdio_probe()`. This file maintains no per-device state; the SDIO transport allocates `struct rtw_dev` plus `struct rtw_sdio`.

Dependencies and integration: includes MMC SDIO headers, `main.h`, `rtw8822c.h`, and `sdio.h`. It is the connection point between board SDIO enumeration and common rtw88/mac80211 registration.

Risks and test signals: primary risks are missing platform enumeration, wrong ID constants, and power-management callback mismatches. Test through module alias inspection, SDIO card probe, firmware load, RX/TX traffic, and host suspend with `MMC_PM_KEEP_POWER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822cu.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822cu.c

Purpose: USB module glue for RTL8822CU-compatible devices. It lists Realtek and OEM USB IDs and binds them to the shared 8822C hardware spec through the rtw88 USB transport.

Important APIs/types: `rtw_8822cu_id_table`, `MODULE_DEVICE_TABLE(usb, ...)`, `rtw8822cu_probe()`, and `struct usb_driver rtw_8822cu_driver`. The table covers Realtek IDs `0xc82c`, `0xc812`, `0xc82e`, `0xd820`, `0xd82b`, plus Alpha and D-Link aliases.

Control flow and state: USB core matching invokes `rtw8822cu_probe()`, which simply delegates to `rtw_usb_probe()`. Disconnect delegates to `rtw_usb_disconnect()`. No local state persists beyond the static ID table and module registration.

Dependencies and integration: depends on Linux USB core, `main.h`, `rtw8822c.h`, and `usb.h`. Integration with mac80211, firmware, endpoint parsing, URB lifecycle, and power sequencing is in `usb.c`.

Risks and test signals: risks are ID table omissions, interface-class matching too broad/narrow, and incorrect `driver_info`. Test by checking USB modaliases, probing each listed VID/PID where available, and verifying firmware load and TX/RX over USB2/USB3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw8822cu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw88xxa.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw88xxa.c

Purpose: shared RTL8821A/8811A/8812A hardware support for rtw88, especially USB-attached 88xxa chips. It owns EFUSE interpretation, USB-oriented power-on/off, LLT and queue setup, RF/BB initialization, channel/band switching, PHY status parsing, TX power programming, false alarm counters, IQK helpers, thermal power tracking, and CCK packet detection control.

Important APIs/functions: exported entry points include `rtw88xxa_efuse_grant`, `rtw88xxa_read_efuse`, `rtw88xxa_power_on`, `rtw88xxa_power_off`, `rtw88xxa_phy_read_rf`, `rtw88xxa_set_channel`, `rtw88xxa_query_phy_status`, `rtw88xxa_set_tx_power_index`, `rtw88xxa_false_alarm_statistics`, IQK backup/restore/configure helpers, `rtw88xxa_iqk_finish`, `rtw88xxa_phy_pwrtrack`, and `rtw88xxa_phy_cck_pd_set`.

Control flow: power-on checks `RTW_FLAG_POWERON`, runs HCI setup, resets partially initialized hardware, executes chip power sequence, configures FIFO/LLT, waits/downloads firmware, loads MAC/BB/RF tables, configures queues, EDCA, aggregation, ARFR, security, PHY/DM, coexistence, then starts HCI. Power-off stops HCI, disables interrupts/RX, runs LPS/off sequences, resets MCU, and clears power state. Channel setting first switches band-specific RFE/basic-rate/CCK behavior, then writes RF channel and bandwidth registers.

State and persistence: mutates `rtwdev->efuse`, `hal`, `fifo`, `dm_info`, `flags`, register state, firmware state, and RF path configuration. EFUSE-derived RFE and USB capabilities persist in memory for later PHY decisions.

Dependencies and integration: depends heavily on `main.h`, `mac.h`, `phy.h`, `coex.h`, `efuse.h`, `usb.h`, register definitions, chip table loaders, firmware helpers, and common HCI ops. It is called from chip ops and supplies shared behavior to 8821A/8812A USB variants.

Risks and test signals: high risk areas are power sequencing timeouts, EFUSE/RFE misclassification, USB2/USB3 quirks, channel/band register programming, single-stream overrides, and thermal tracking boundaries. Test signals include successful firmware download, association on 2.4/5 GHz at 20/40/80 MHz, RF path reporting, stable suspend/remove, valid RSSI/EVM, tx power compliance, and no LLT/RF polling errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw88xxa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw88xxa.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw88xxa.h

Purpose: public declarations and hardware-layout definitions for the rtw88 88xxa common implementation. It defines packed EFUSE layouts, Jaguar PHY status words, bit masks, beacon timing constants, and exported function prototypes.

Important APIs/types: `struct rtw8821au_efuse`, `struct rtw8812au_efuse`, and `struct rtw88xxa_efuse` model the 512-byte logical EFUSE image and include a `static_assert` on size. `struct rtw_jaguar_phy_status_rpt` maps PHY status words `w0` through `w6`; many `RTW_JGRPHY_*` masks extract gain, channel, CFO, EVM, SNR, antenna, and CCK fields. `RF18_BW_MASK` and exported function prototypes form the compile-time contract for chip-specific files.

Control flow and state: no executable flow beyond declarations. Its state model is the binary interpretation of EFUSE and RX PHY report data consumed by `rtw88xxa.c`.

Dependencies and integration: includes byteorder and register definitions. It is included by common code and 88xxa chip files to keep EFUSE parsing, PHY status parsing, and chip ops consistent.

Risks and test signals: packed layout or bit-mask errors silently corrupt MAC address, regulatory, power, antenna, or RSSI interpretation. Test by validating `static_assert`, comparing EFUSE dumps against vendor docs, and checking RX status metrics and MAC address on 8821AU/8812AU hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rtw88xxa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rx.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rx.c

Purpose: common rtw88 receive descriptor parsing, mac80211 RX status population, RX statistics accounting, RSSI/EVM/SNR update, and scan-time channel correction.

Important APIs/functions: `rtw_rx_stats()` accounts unicast data bytes globally and per VIF. `rtw_rx_query_rx_desc()` decodes `struct rtw_rx_desc`, identifies C2H packets, locates PHY status and 802.11 header, calls chip-specific `query_phy_status`, and fills `ieee80211_rx_status`. `rtw_update_rx_freq_from_ie()` corrects scan result channel/frequency from beacon/probe-response IEs when packet status has an invalid channel.

Control flow: HCI RX paths pass a descriptor pointer into `rtw_rx_query_rx_desc()`. For non-C2H frames it decodes length/error/encryption/rate/bandwidth/TSF, optionally parses PHY status, builds mac80211 rate/encoding/signal fields, updates address-matched PHY statistics, and leaves the caller to deliver the skb. Address matching iterates active VIFs by BSSID and destination/beacon rules.

State and persistence: updates `rtwdev->stats`, per-VIF stats, `dm_info` packet counters/EWMA metrics, station average RSSI, and `pkt_stat`/`rx_status` transient state. No durable storage is used.

Dependencies and integration: depends on mac80211/cfg80211 helpers, `fw.h` for scan-offload feature checks, `ps.h`, `debug.h`, `util.h` inline BSSID selection, and chip `query_phy_status`.

Risks and test signals: descriptor offset math is safety-critical for aggregated USB/SDIO packets. Rate-to-mac80211 mapping, scan channel correction, and C2H bypass are key risks. Test with RX under scan/offload, encrypted traffic, malformed descriptor fuzzing, and monitor RSSI/rate fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rx.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rx.h

Purpose: declares the common RX descriptor ABI and exported receive helpers for rtw88 transports.

Important APIs/types: `enum rtw_rx_desc_enc` maps hardware encryption codes; `struct rtw_rx_desc` is a packed six-word descriptor; `RTW_RX_DESC_W*` masks define packet length, CRC/ICV, driver-info size, encryption type, shift, PHY status, SW-decrypt bit, MAC ID, C2H marker, PPDU count, rate, bandwidth, and TSF. Function prototypes expose `rtw_rx_stats`, `rtw_rx_query_rx_desc`, and `rtw_update_rx_freq_from_ie`.

Control flow and state: no runtime code except `rtw_update_rx_freq_for_invalid()`, which calls IE-based channel correction only when `pkt_stat->channel_invalid` is set. State is carried by caller-owned `struct rtw_rx_pkt_stat` and `ieee80211_rx_status`.

Dependencies and integration: included by USB, SDIO, PCI, and core receive paths. Its masks must match firmware/hardware descriptor format and the parser in `rx.c`.

Risks and test signals: any bit-mask or descriptor-size mismatch causes corrupted packet length, wrong C2H routing, bogus rates, or memory overrun in HCI RX loops. Test by validating RX descriptor dumps against expected fields, running encrypted and C2H traffic, and checking aggregated packet parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sar.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sar.c

Purpose: implements cfg80211 SAR power-limit support for rtw88. It converts userspace/regulatory SAR power specs into per-RF-path/per-rate-section power offsets used by PHY TX power programming.

Important APIs/functions: `rtw_query_sar()` returns the active SAR limit for a path/rate/band argument or the chip maximum when no SAR source is active. `rtw_set_sar_specs()` validates `NL80211_SAR_TYPE_POWER`, converts each cfg80211 frequency-range sub-spec through `rtw_sar_to_phy()`, and applies it via `rtw_apply_sar()`. `rtw_sar_capa` exposes four common frequency ranges.

Control flow: a cfg80211 SAR request is expanded across all `RTW_RF_PATH_MAX` paths and `RTW_RATE_SECTION_NUM` rate sections. The conversion accounts for cfg80211's 0.25 dBm factor, chip TX gain index factor, chip max power index, and current base power tables before reprogramming TX power for the current channel.

State and persistence: mutates `rtwdev->hal.sar`, including source and per-path/rate/common-band arrays. Source locking prevents replacing an active non-`NONE` source with a different source.

Dependencies and integration: depends on `phy.h` for `rtw_phy_set_tx_power_level()` and base tables in `hal`. Integrated with cfg80211 SAR capability advertisement.

Risks and test signals: risks include unit conversion mistakes, invalid band index handling, and source contention returning `-EBUSY`. Test with cfg80211 SAR commands, inspect power table changes per band, and verify regulatory power limits with RF measurements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sar.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sar.h

Purpose: public SAR interface for rtw88. It defines the power-unit conversion factor and the argument structure used to query per-rate/per-path SAR limits.

Important APIs/types: `RTW_COMMON_SAR_FCT` documents cfg80211 `NL80211_SAR_TYPE_POWER` units as 2 fractional bits. `struct rtw_sar_arg` contains `sar_band`, `path`, and `rs` rate-section indexes. The header declares `rtw_sar_capa`, `rtw_query_sar()`, and `rtw_set_sar_specs()`.

Control flow and state: no runtime flow. The state contract is that callers supply indexes matching rtw88 SAR band/rate/path enums and receive an s8 PHY power adjustment.

Dependencies and integration: includes `main.h` for core rtw88 types and is consumed by regulatory/cfg80211 setup and PHY TX power calculation code.

Risks and test signals: the main risk is caller/index mismatch because the struct is compact and unvalidated at query time beyond source handling. Build coverage plus exercising cfg80211 SAR set/query paths and verifying `rtw_sar_capa` range count are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sdio.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sdio.c

Purpose: SDIO HCI implementation for rtw88. It provides register access, firmware/H2C/reserved-page writes, RX FIFO draining, TX queueing, interrupt handling, power-save hooks, probe/remove/shutdown, and `rtw_hci_ops` for SDIO devices.

Important APIs/functions: exported `rtw_sdio_probe`, `rtw_sdio_remove`, `rtw_sdio_shutdown`, and `rtw_sdio_pm_ops`. Core internal functions include direct/indirect read/write helpers, `rtw_sdio_read_port`, `rtw_sdio_write_port`, `rtw_sdio_check_free_txpg`, RX aggregation setup, IRQ handler `rtw_sdio_handle_interrupt`, TX worker `rtw_sdio_tx_handler`, and HCI ops `rtw_sdio_ops`.

Control flow: probe allocates `ieee80211_hw` plus `rtw_sdio`, initializes core, claims/enables the SDIO function, initializes IRQ mask and TX workqueue, sets chip info, claims SDIO IRQ, then registers mac80211 hardware. Interrupts read/ack HISR, handle TX errors and RX requests, drain RX lengths up to a 64 KiB budget, split aggregated frames, route C2H or mac80211 RX, and clear status. TX writes prepare descriptors, enqueue by hardware queue, and a single-thread workqueue drains queues with free-page checks and retry-by-requeue.

State and persistence: owns `struct rtw_sdio` fields: SDIO function, IRQ mask, RX address counter, SDIO3 mode, current IRQ thread marker, TX workqueue, work data, and per-queue skb queues. It mutates power flags for deep leisure PS.

Dependencies and integration: depends on Linux MMC/SDIO APIs, rtw88 core/mac/firmware/power/RX/TX helpers, and chip-specific page-size/free-page semantics.

Risks and test signals: high-risk areas are host-claim recursion in IRQ context, indirect register access when powered off, unaligned SDIO buffers, RX aggregation split bounds, TX free-page retry behavior, and removal while work/IRQ is active. Test with SDIO3 and non-SDIO3 hosts, suspend/resume, traffic under low TX pages, C2H events, and remove/shutdown races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sdio.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sdio.h

Purpose: SDIO register map, constants, state structures, and public probe/remove declarations for the rtw88 SDIO HCI.

Important APIs/types: defines SDIO bus-domain offsets, host interrupt mask/status registers, indirect register access registers, command address encodings, block size, RX FIFO address macro, and 8-byte data pointer alignment. `struct rtw_sdio` holds the SDIO function, IRQ mask, RX address, SDIO3 mode, IRQ-thread marker, TX workqueue, work item, and TX skb queues. `struct rtw_sdio_tx_data` stores TX report sequence number in skb driver data.

Control flow and state: no complex runtime flow except `rtw_sdio_is_sdio30_supported()`, which reads `sdio3_bus_mode` from private HCI state. The register constants direct all read/write and FIFO operations in `sdio.c`.

Dependencies and integration: includes forward declarations for `sdio_func` and `sdio_device_id`, exports `rtw_sdio_pm_ops`, and declares SDIO lifecycle functions used by chip glue modules such as `rtw8822cs.c`.

Risks and test signals: register offset and bit-mask correctness are critical. State layout must fit the `ieee80211_alloc_hw(sizeof(rtw_dev)+sizeof(rtw_sdio))` allocation model. Test through compilation, SDIO IRQ/RX/TX operation, and descriptor alignment checks on strict hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sdio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sec.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sec.c

Purpose: manages rtw88 hardware security CAM allocation, programming, clearing, backup enumeration, and security engine enablement.

Important APIs/functions: `rtw_sec_get_free_cam()` chooses the next free CAM slot, reserving the first four entries when default-key search is enabled. `rtw_sec_write_cam()` fills an eight-word CAM entry with key index, cipher type, group/pairwise flag, valid bit, station/broadcast address, and key bytes. `rtw_sec_clear_cam()` invalidates one CAM entry. `rtw_sec_cam_pg_backup()` lists used CAM IDs for page backup. `rtw_sec_enable_sec_engine()` enables MAC security and default-key search bits.

Control flow: mac80211 key installation selects/free CAM indexes, writes content through `RTW_SEC_WRITE_REG`/`RTW_SEC_CMD_REG`, and updates the driver's shadow `cam_table` and `cam_map`. Enabling security toggles `REG_CR` and `RTW_SEC_CONFIG`.

State and persistence: persistent in-memory state is `rtw_sec_desc` shadow CAM map/table and `default_key_search`; hardware state is the CAM and security engine registers. Keys are referenced via `ieee80211_key_conf`.

Dependencies and integration: depends on rtw88 core structures, `sec.h` registers, and Linux key/cipher metadata. TX/RX descriptor paths use the installed key state for hardware crypto.

Risks and test signals: risks include CAM slot leaks, wrong group/pairwise address, unsupported cipher mapping, and stale CAM entries after key removal. Test with WEP/TKIP/CCMP association, group rekey, pairwise rekey, multi-VIF keys, and suspend/resume CAM backup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sec.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sec.h

Purpose: declares security CAM registers, command/config bits, and exported security helpers for rtw88.

Important APIs/types: constants include `RTW_SEC_CMD_REG`, `RTW_SEC_WRITE_REG`, `RTW_SEC_READ_REG`, `RTW_SEC_CONFIG`, CAM entry shift, default-key count, write/clear/poll command bits, TX/RX decrypt enable bits, default-key search bits, and `RTW_SEC_ENGINE_EN`. Prototypes expose CAM allocation, write, clear, backup, and engine enable functions.

Control flow and state: no local runtime flow. The constants define how `sec.c` builds CAM write commands and toggles MAC security features.

Dependencies and integration: included wherever rtw88 key installation, hardware crypto, or WoWLAN CAM backup needs security register definitions. It depends on core `struct rtw_dev`, `rtw_sec_desc`, mac80211 station/key types through included headers.

Risks and test signals: register-bit mistakes can disable encryption/decryption or corrupt CAM. Test by compiling all users, verifying encrypted traffic offload, checking CAM backup counts, and validating key removal clears hardware entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/sec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/tx.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/tx.c

Purpose: common transmit preparation for rtw88. It translates mac80211 SKBs into hardware TX packet info/descriptors, manages TX reports, reserved/H2C packet allocation, mac80211 TXQ draining, aggregation decisions, statistics, and queue mapping.

Important APIs/functions: `rtw_tx_fill_tx_desc()` encodes `struct rtw_tx_pkt_info` into the hardware descriptor. `rtw_tx_pkt_info_update()` derives MAC ID, management/data rates, AMPDU parameters, RTS, BW, STBC/LDPC, security type, queue select, report request, size, and stats. `rtw_tx()` submits a single SKB to HCI ops. TXQ functions initialize/cleanup/drain mac80211 TXQs. `rtw_tx_report_enqueue/handle/purge_timer` bridge firmware CCX reports to mac80211 TX status. Reserved page helpers allocate SKBs for firmware pages and H2C.

Control flow: mac80211 TX calls update packet info, HCI `tx_write`, and HCI kick-off. TXQ work locks `txq_lock`, dequeues frames from mac80211, checks/requests BA aggregation, writes to HCI, then kicks HCI. TX reports store sequence numbers in skb driver data and are matched against C2H report payloads.

State and persistence: updates global/per-VIF TX stats, `rtwdev->tx_report` queue/timer/SN, station BA bitmaps, and transient descriptor fields. Persistent queue membership lives in `rtwdev->txqs` and HCI queues.

Dependencies and integration: depends on mac80211 TX info, firmware C2H definitions, power-save code, and HCI ops implemented by PCI/USB/SDIO.

Risks and test signals: descriptor bit-field correctness, TX status lifetime, queue mapping, forced-rate/debug paths, and AMPDU negotiation are key risks. Test with unicast/multicast, management frames, BA setup, encryption, TX status requests, queue cleanup, and all HCIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/tx.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/tx.h

Purpose: declares the rtw88 TX descriptor format, queue-select values, TX helper APIs, and descriptor checksum helper.

Important APIs/types: `struct rtw_tx_desc` is a packed ten-word hardware descriptor. `RTW_TX_DESC_W*` masks encode packet size, offset, BMC, MAC ID, QSEL, rate ID, security type, aggregation, report, RTS, fixed rate, data rate, BW, LDPC/STBC, checksum, hardware sequence, software sequence, and TIM offset. `enum rtw_tx_desc_queue_select` maps TIDs, beacon, high, management, and H2C queue selects.

Control flow: `fill_txdesc_checksum_common()` clears and recomputes the descriptor checksum over 16-bit words. `rtw_tx_fill_txdesc_checksum()` delegates to chip ops, allowing chip-specific checksum behavior while preserving the common call site.

State and persistence: no persistent state. The header defines on-wire/on-DMA descriptor state used by all HCI transmit paths.

Dependencies and integration: included by common TX plus USB/SDIO transports. It depends on `struct rtw_dev`, `struct rtw_tx_pkt_info`, mac80211 TX types, and chip ops.

Risks and test signals: descriptor ABI mistakes produce firmware drops, wrong queueing, bad rates, or checksum failures. Test with descriptor dumps, H2C/reserved pages, TX over each access category, and chip-specific checksum validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/usb.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/usb.c

Purpose: USB HCI implementation for rtw88. It provides vendor control register access, firmware page download, endpoint parsing, TX/RX URB management, TX aggregation, RX aggregation parsing, USB2/USB3 mode switching, PHY interface tuning, lifecycle probe/disconnect, and `rtw_hci_ops`.

Important APIs/functions: exported `rtw_usb_probe()` and `rtw_usb_disconnect()`. Core helpers include `rtw_usb_read/write*`, `rtw_usb_write_firmware_page`, `rtw_usb_parse`, `rtw_usb_tx_agg_skb`, `rtw_usb_tx_handler`, `rtw_usb_rx_handler`, `rtw_usb_rx_resubmit`, dynamic RX aggregation functions, USB mode switching helpers, `rtw_usb_phy_cfg`, and HCI ops `rtw_usb_ops`.

Control flow: probe allocates `ieee80211_hw` plus `rtw_usb`, preallocates RX URBs, initializes core/interface/TX/RX workqueues, sets chip info, applies USB PHY parameters, optionally triggers USB3 mode switching by disconnecting/re-enumerating, registers hardware, then submits RX URBs. TX pushes descriptors onto endpoint queues, workqueue aggregates SKBs up to chip limits and submits bulk URBs, then reports status or waits for firmware TX report. RX completion queues filled SKBs, resubmits URBs, and workqueue splits aggregated descriptors into C2H or mac80211 RX frames.

State and persistence: owns `rtw_usb` state: device pointer, register bounce buffer ring protected by spinlock, endpoint maps, TX/RX workqueues, TX endpoint queues, RX control blocks, RX queue/free queue. Module parameter `switch_usb_mode` persists policy for USB3 switching.

Dependencies and integration: depends on Linux USB core, rtw88 TX/RX/FW/MAC/PS helpers, chip RQPN/intf tables, and mac80211.

Risks and test signals: high-risk areas are URB lifetime on disconnect, queue index validation, TX aggregation skb ownership, RX length bounds, control-transfer errors, USB3 re-enumeration, and reset during disconnect. Test USB2/USB3 probe, unplug under traffic, suspend/resume, large RX aggregation, TX status requests, and endpoint variants with one to four bulk-out pipes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/usb.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/usb.h

Purpose: USB constants, private state structures, and exported lifecycle declarations for rtw88 USB HCI.

Important APIs/types: defines vendor request constants, Realtek USB VID, buffer sizes, RX/TX ring counts, endpoint count, queue-select max, receive buffer alignment/size, and firmware address constants. `struct rx_usb_ctrl_block` ties each RX URB to an skb and device. `struct rtw_usb_tx_data` stores TX report sequence number in skb driver data. `struct rtw_usb` stores USB device, register bounce buffers, endpoint mapping, TX/RX workqueues, TX queues, RX URBs, and RX skb queues. `rtw_get_usb_priv()` and `rtw_usb_get_tx_data()` are inline accessors.

Control flow and state: no complex flow beyond accessors and `BUILD_BUG_ON` validation that USB TX metadata fits mac80211 skb driver data. State layout is consumed by `usb.c` after `ieee80211_alloc_hw()` allocates private memory.

Dependencies and integration: included by chip USB glue modules and `usb.c`. It forms the private HCI ABI for rtw88 USB.

Risks and test signals: buffer constants directly bound URB transfer sizes and aggregation behavior; wrong limits can cause truncation or memory pressure. Test via compile-time metadata fit, stress RX/TX aggregation, and probe devices with different endpoint layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/util.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/util.c

Purpose: small shared utility layer for rtw88 hardware polling, LTE coexistence register access, register restoration, descriptor-rate conversion, and safe non-atomic iteration over stations/VIFs.

Important APIs/functions: `check_hw_ready()` polls a masked register for up to 1000 iterations with 10 us delay. `ltecoex_read_reg()` and `ltecoex_reg_write()` use chip LTE coexistence control/data registers after readiness polling. `rtw_restore_reg()` restores a table of 1/2/4-byte backup registers. `rtw_desc_to_mcsrate()` maps descriptor rate IDs into mac80211 MCS/NSS. `rtw_iterate_stas()` and `rtw_iterate_vifs()` collect atomic mac80211 iteration results into temporary lists, then call a non-atomic callback while `rtwdev->mutex` is held.

Control flow: polling helpers are synchronous. Iteration helpers allocate list entries with `GFP_ATOMIC` in the mac80211 atomic iterator, then process and free them outside the iterator, relying on the caller-held mutex to prevent removal.

State and persistence: no persistent state beyond temporary lists. Register helpers mutate hardware, and rate conversion mutates caller-provided output pointers.

Dependencies and integration: used by WoWLAN pattern CAM polling, LTE coexistence code, IQK/register restore paths, RX status filling, and firmware media/key iteration helpers.

Risks and test signals: risks include silent iteration entry allocation failure, required mutex not held, unsupported backup lengths ignored, and timeout-sensitive polling. Test with lockdep, hardware timeout injection, LTE coexistence paths, and RX rate mapping for HT/VHT rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/util.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/util.h

Purpose: utility declarations and inline/macros for rtw88 iteration and 802.11 BSSID extraction.

Important APIs/types: macros wrap atomic mac80211 iterators for active interfaces, stations, and keys: `rtw_iterate_vifs_atomic`, `rtw_iterate_stas_atomic`, `rtw_iterate_keys`, and `rtw_iterate_keys_rcu`. Prototypes expose non-atomic `rtw_iterate_vifs()` and `rtw_iterate_stas()`. `get_hdr_bssid()` chooses addr1 for ToDS, addr2 for FromDS, otherwise addr3.

Control flow and state: `get_hdr_bssid()` is a small frame-control branch used by RX address matching. The iterator macros forward directly into mac80211 and do not add state.

Dependencies and integration: included by RX, WoWLAN, firmware/key paths, and other code needing station/VIF/key iteration. It depends on mac80211 frame helpers and `struct rtw_dev`.

Risks and test signals: incorrect BSSID selection breaks per-VIF RX stat/RSSI updates, especially in AP/client direction cases. Iterator choice matters for locking context. Test with station and AP modes, ToDS/FromDS frames, lockdep, and key iteration during WoWLAN setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/wow.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/wow.c

Purpose: Wake-on-WLAN support for rtw88. It translates cfg80211 WoWLAN requests into firmware AOAC commands, pattern CAM entries, reserved pages, firmware swapping, power-save transitions, wake reason reporting, and resume restoration.

Important APIs/functions: public `rtw_wow_suspend()` and `rtw_wow_resume()`. Internals cover wake reason reporting, pattern mask translation/CRC/CAM writes, BB/RX-DMA stop/start, firmware status polling, security type iteration, firmware start/stop, reserved-page configuration, normal/WoW firmware swap, PNO request capture, PS leave/enter/restore, wakeup VIF selection, and cleanup.

Control flow: suspend sets wake flags/patterns/PNO and selects one station VIF, leaves normal PS, stops TRX, downloads WoW firmware, sets `RTW_FLAG_WOWLAN`, downloads WoW reserved pages, starts firmware wake controls, stops HCI, restarts BB, protects MAC reset, then enters WoW PS. Resume validates WoW flag, leaves PS, reports wake reason via mac80211, reinitializes HCI, stops firmware wake controls, clears pattern CAM, swaps normal firmware, restores normal reserved pages, restarts RX/BB/watchdog, restores PS, and frees PNO state.

State and persistence: mutates `rtwdev->wow` including selected VIF, pattern array/count, flags, PNO copies, `ips_enabled`, and saved `txpause`; also toggles `RTW_FLAG_WOWLAN` and `RTW_FLAG_LEISURE_PS_DEEP`.

Dependencies and integration: depends on firmware H2C/AOAC APIs, reserved-page builders, mac80211 WoWLAN reporting, PS, MAC/HCI operations, and utility iterators.

Risks and test signals: high-risk areas are firmware swap failures, pattern mask translation from Ethernet to 802.11/LLC layout, unsupported HCI reset avoidance, memory cleanup on partial setup, PNO deep PS behavior, and resume ordering. Test disconnect/magic/pattern/GTK/PNO wake, linked and no-link states, firmware failure injection, suspend/resume over PCI/USB, and leak checks for PNO arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/wow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/wow.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/wow.h

Purpose: public WoWLAN definitions for rtw88 suspend/resume support.

Important APIs/types: `PNO_CHECK_BYTE`, `enum rtw_wow_pattern_type`, `enum rtw_wake_reason`, `struct rtw_fw_media_status_iter_data`, and `struct rtw_fw_key_type_iter_data`. Inline helpers `rtw_wow_mgd_linked()` and `rtw_wow_no_link()` inspect the selected WoW VIF's rtw private net type. Prototypes expose `rtw_wow_suspend()` and `rtw_wow_resume()`.

Control flow and state: the inline helpers assume `rtwdev->wow.wow_vif` is valid and return whether WoW is handling a linked managed station or a no-link station used for PNO. The enums define firmware/hardware wake reason and pattern classifications used in `wow.c`.

Dependencies and integration: depends on `main.h`, mac80211 VIF private state, firmware AOAC command data, and cfg80211 WoWLAN.

Risks and test signals: invalid `wow_vif` use would dereference NULL; callers must set wakeups before invoking linked/no-link helpers. Test suspend rejection with no suitable station VIF, linked WoW, and PNO no-link WoW.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/wow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/Kconfig

Purpose: Kconfig menu for Realtek rtw89 Wi-Fi 6/6E/7 driver support. It defines the top-level `RTW89` menu, core/transport/chip internal symbols, user-selectable adapter modules, and debug options.

Important symbols: `RTW89` depends on `MAC80211`; `RTW89_CORE` selects `WANT_DEV_COREDUMP`; `RTW89_PCI` and `RTW89_USB` are transport internals. Chip internals include `RTW89_8851B`, `8852A`, `8852B_COMMON`, `8852B`, `8852BT`, `8852C`, and `8922A`. User-visible modules cover PCI and USB variants: 8851BE/BU, 8852AE/AU/BE/BU/BTE/CE/CU, and 8922AE. Debug options are `RTW89_DEBUGMSG` and `RTW89_DEBUGFS`.

Control flow and state: build-time dependency selection only. Choosing a device symbol selects core, transport, and chip support so the Makefile can link the corresponding objects.

Dependencies and integration: integrates with Linux kernel Kconfig, mac80211, PCI/USB subsystems, cfg80211 debugfs, and Makefile object lists.

Risks and test signals: dependency mistakes produce missing symbols or modules without required transport/core code. Test with `allmodconfig`, individual device configs, PCI-only/USB-only builds, and debugfs-disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/Makefile

Purpose: builds rtw89 core, chip, bus, and debug modules according to Kconfig symbols.

Important targets: `rtw89_core.o` includes core, mac80211, MAC/PHY, firmware, CAM, EFUSE, regulatory/SAR, coexistence, power-save, channel, SER, ACPI, and util objects; PM adds `wow.o`. Chip modules aggregate chip logic, tables, RFK, and RFK tables for 8851B/8852A/8852B/8852BT/8852C/8922A. Interface modules include per-device PCI/USB glue objects and transport modules `rtw89_pci.o` (`pci.o`, `pci_be.o`) and `rtw89_usb.o` (`usb.o`).

Control flow and state: no runtime flow; it maps Kconfig booleans/tristates to object composition. The ordering ensures common support is available before chip/interface modules at link time.

Dependencies and integration: coupled tightly to `Kconfig` symbol names and source-file names. Debug object inclusion depends on `CONFIG_RTW89_DEBUG`.

Risks and test signals: missing object entries cause unresolved symbols; stale entries cause build failures. Test by building each Kconfig combination, especially PM on/off, debug on/off, USB-only, PCI-only, and Wi-Fi 7 8922A.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/acpi.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/acpi.c

Purpose: ACPI integration for rtw89 regulatory and SAR policy. It evaluates Realtek DSM functions and ACPI methods, validates binary policy signatures, flattens ACPI packages/buffers into driver data, recognizes HP/Realtek SAR table formats, applies geographic SAR deltas, and exposes static/dynamic SAR configuration to the rtw89 regulatory/SAR layer.

Important APIs/functions: `rtw89_acpi_evaluate_dsm()` handles DSM functions including 6 GHz baseline policy, standard-power support, VLP support, TAS, regulatory rules, and integer values. `rtw89_acpi_evaluate_rtag()` reads antenna gain. `rtw89_acpi_sar_get_subband()` and `rtw89_acpi_sar_subband_to_band()` map frequencies/subbands. SAR loaders normalize HP and RT formats, load legacy/6 GHz standard and small tables, apply geo-SAR, and `rtw89_acpi_evaluate_sar()` coordinates static/dynamic SAR recognition and indicator setup. `rtw89_acpi_evaluate_dynamic_sar_indicator()` polls table selection changes.

Control flow: ACPI evaluation first finds a device-root method or DSM object, flattens nested integers/buffers/packages, validates expected type/length/signature, then copies policy buffers. SAR evaluation prefers static SAR, falls back to dynamic SAR, recognizes CID/revision/table length, loads tables into all regulatory domains, optionally applies GEO SAR per regulatory type, initializes 2TX downgrade and indicator fields, then fetches dynamic table selection if needed.

State and persistence: allocates temporary ACPI data/policy copies for callers; fills caller-owned `rtw89_sar_cfg_acpi` tables, valid count, downgrade value, and indicator fields. No global mutable state beyond the Realtek GUID.

Dependencies and integration: depends on Linux ACPI/UUID APIs and rtw89 ACPI/debug/type definitions. It feeds rtw89 SAR, regulatory, TAS, 6 GHz policy, and antenna-gain logic.

Risks and test signals: risks include malformed firmware ACPI objects, divide-by-zero if table count were zero, signature/length mismatch, regulatory mapping gaps, and stale dynamic SAR indicators. Test with systems exposing HP and Realtek SAR variants, ACPI fuzz/malformed methods, 6 GHz policy DSMs, geo regulatory changes, and dynamic SAR polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/acpi.c -->
