# subset-b-004900 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/debug.c

## Purpose

`debug.c` provides the optional debug and observability surface for the Realtek `rtw88` wireless driver. Under `CONFIG_RTW88_DEBUGFS`, it builds a `debugfs` directory named `rtw88` below the wiphy debugfs root and exposes register dumps, arbitrary MAC/BB/RF reads and writes, firmware H2C injection, reserved-page FIFO dumps, security CAM dumps, PHY statistics, coexistence controls, EDCCA toggling, firmware crash triggering, fixed-rate control, and dynamic-mechanism capability masking. Under `CONFIG_RTW88_DEBUG`, it also implements the exported `rtw_dbg()` logging helper gated by the global debug mask.

## Important APIs, Types, and Functions

The central private type is `struct rtw_debugfs_priv`. Each debugfs file stores a back pointer to `struct rtw_dev`, optional read and write callbacks, and a small union of callback-specific state such as register address/length, RF path/address/mask, reserved-page offset/count, CAM entry index, or selected dynamic-mechanism capability bit.

`struct rtw_debugfs` is a per-device aggregate of these private objects. `rtw_debugfs_templ` initializes callback mappings for all exposed files, and `rtw_debugfs_init()` `kmemdup()`s the template into `rtwdev->debugfs` before registering files. `rtw_debugfs_deinit()` only frees that allocation; debugfs dentry lifetime is left to the surrounding wiphy/device teardown.

Notable debugfs file handlers include:

- `rtw_debugfs_get_read_reg()` and `rtw_debugfs_set_read_reg()` for staged 8/16/32-bit MMIO reads.
- `rtw_debugfs_set_write_reg()` for raw MMIO writes through `rtw_write8/16/32`.
- `rtw_debugfs_get_rf_read()`, `rtw_debugfs_set_rf_read()`, `rtw_debugfs_set_rf_write()`, and `rtw_debugfs_get_rf_dump()` for RF register access under `rtwdev->mutex`.
- `rtw_debugfs_set_h2c()` for manually sending an eight-byte firmware command via `rtw_fw_h2c_cmd_dbg()`.
- `rtw_debugfs_get_dump_cam()` for reading a selected security CAM entry through `RTW_SEC_CMD_REG`.
- `rtw_debugfs_get_rsvd_page()` and `rtw_debugfs_set_rsvd_page()` for dumping firmware reserved pages via `rtw_fw_dump_fifo()`.
- `rtw_debugfs_get_tx_pwr_tbl()` for reporting per-path/rate power table values and regulatory/offset/limit/SAR inputs.
- `rtw_debugfs_get_phy_info()` and exported `rtw_debugfs_get_simple_phy_info()` for link, throughput, rate, RSSI, EVM, SNR, CFO, and packet counter summaries.
- `rtw_debugfs_set_coex_enable()`, `rtw_debugfs_get_coex_info()`, `rtw_debugfs_set_edcca_enable()`, `rtw_debugfs_set_fw_crash()`, `rtw_debugfs_set_force_lowest_basic_rate()`, and `rtw_debugfs_set_dm_cap()` for mutable runtime debug controls.

## Control Flow

Open/read/write flow is intentionally small. Read-only and read-write files use `single_open()` with `rtw_debugfs_single_show()`, which dispatches to the stored `cb_read`. Read-write files receive writes through `rtw_debugfs_single_write()`, which unwraps the `seq_file` private pointer before dispatching to `cb_write`. Write-only files use `simple_open()` and `rtw_debugfs_common_write()`, where `filp->private_data` is already the callback state.

Initialization copies the static template, creates the top directory, and calls three registration groups. `rtw_debugfs_add_basic()` creates active control and summary nodes. `rtw_debugfs_add_sec0()` and `rtw_debugfs_add_sec1()` create fixed MAC and BB page dump nodes, with additional 8822C BB pages in section 1. The page dump callbacks iterate a 0x100-byte register window in 32-bit steps.

Most setters parse small user strings through `kstrto*()` or `rtw_debugfs_copy_from_user()` plus `sscanf()`, store state in the debugfs private union, and return the byte count on success. Stateful readbacks then use that stored state on subsequent reads. Several operations that touch RF, firmware command paths, coexistence state, restart state, or security CAMs take `rtwdev->mutex`; simple MAC/BB register dumping does not.

The firmware-crash control is a deliberate restart path. Writing true leaves deep LPS, sets `RTW_FLAG_RESTART_TRIGGERING`, writes `REG_HRCV_MSG`, and refuses to run while `RTW_FLAG_RESTARTING` is already set. Dynamic mechanism capability control interprets a positive number as enable and a negative number as disable by clearing or setting a bit in `dm_info->dm_flags`, then a read of `dm_cap` either dumps TXGAPK status or lists all capabilities.

## State and Persistence

Debugfs state persists in `rtwdev->debugfs` for the device lifetime. The per-file private union stores the latest input for staged reads, CAM selection, reserved-page ranges, and dynamic-mechanism status selection. Writes can persistently alter driver and hardware state: fixed rate is stored in `dm_info->fix_rate`; coexistence manual control is stored in `coex->manual_control`; EDCCA uses the global `rtw_edcca_enabled` and reapplies PHY adaptivity mode; lowest-basic-rate forcing changes `rtwdev->flags`; raw register/RF writes directly modify hardware; and firmware crash writes trigger recovery state.

The report-oriented reads sample live state rather than caching. The TX power table locks `hal->tx_power_mutex` while walking `hal->tx_pwr_tbl`, and PHY information reads from current `dm_info`, `hal`, `stats`, and ewma fields. Reserved-page dumps allocate a temporary buffer with `vzalloc()` and free it after formatting.

## Dependencies and Integration Points

This file depends on Linux debugfs, `seq_file`, user-copy helpers, Realtek register accessors from `hci.h`, firmware helpers from `fw.c`, security CAM helpers, coexistence display/control functions, PHY adaptivity, power-save exit helpers, regulatory helpers, and driver-wide structures from `main.h`. It is only compiled when the relevant config options are enabled, while `debug.h` provides no-op stubs for non-debug builds.

Debugfs operations intentionally bypass normal high-level policy in several places. The raw write nodes are maintenance tools and can modify any accessible MAC/BB/RF register. H2C injection bypasses typed command constructors in `fw.c`. Firmware crash injection integrates with the recovery path by setting restart flags and poking the firmware receive-message register.

## Risks

The largest risk is that writable debugfs nodes are powerful. Incorrect `write_reg`, `rf_write`, or `h2c` input can corrupt hardware state, violate sequencing assumptions, or trigger firmware behavior not expected by normal driver paths. Most parsers cap input to 32 bytes but otherwise trust numeric values, including register addresses and RF masks.

Some debugfs reads can be expensive or disruptive. Full RF dumps iterate every path and 0x100 RF addresses under the device mutex. Reserved-page dumping allocates `page_num * page_size` without a local upper bound beyond user input and firmware FIFO validation. Register dump nodes perform many direct MMIO reads without taking the device mutex.

Mutable diagnostic flags can affect normal operation. EDCCA toggling changes PHY adaptivity, fixed-rate control changes rate selection, force-lowest-basic-rate changes transmit policy, and coexistence manual control disables the normal coexistence mechanism. Tests that use these nodes must restore state afterward.

## Test Signals

Useful validation includes enabling `CONFIG_RTW88_DEBUGFS` and verifying that each debugfs file is created, readable/writable with valid input, and returns `-EINVAL` or `-EFAULT` on malformed input. Hardware tests should verify MAC/BB page dumps, RF read/write round trips under mutex, reserved-page dumps on chips with FIFO dump support, CAM dumping after key install, TX power table output across 2.4/5 GHz and bandwidth changes, and firmware crash recovery. `CONFIG_RTW88_DEBUG` builds should confirm `rtw_dbg()` emits only when `rtw_debug_mask` contains the requested mask.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/debug.h

## Purpose

`debug.h` defines the public debug interface used throughout `rtw88`. It provides debug mask bits, conditional prototypes or stubs for debugfs helpers, the conditional `rtw_dbg()` logging API, and always-available `rtw_info`, `rtw_warn`, and `rtw_err` wrappers around device logging.

## Important APIs, Types, and Functions

`enum rtw_debug_mask` assigns one bit per debug category, including PCI, TX, RX, PHY, firmware, efuse, coexistence, RF calibration, regulatory, debugfs, power save, beamforming, WoWLAN, CFO, path diversity, adaptivity, hardware scan, state, SDIO, USB, unexpected events, and all-events. These masks are consumed by `rtw_dbg()` and `rtw_dbg_is_enabled()`.

When `CONFIG_RTW88_DEBUGFS` is enabled, the header declares `rtw_debugfs_init()`, `rtw_debugfs_deinit()`, and `rtw_debugfs_get_simple_phy_info()`. Without it, init/deinit become inline no-ops. When `CONFIG_RTW88_DEBUG` is enabled, `rtw_dbg()` is declared with printf checking and `rtw_dbg_is_enabled()` tests the global `rtw_debug_mask`; otherwise both compile to no-op/false.

## Control Flow

This header has no runtime control flow of its own beyond inline gating. Callers can invoke debugfs init/deinit unconditionally and let config stubs collapse away. Debug logging calls similarly compile in all call sites but become no-ops when debug support is disabled.

## State and Persistence

The only state referenced here is the external `rtw_debug_mask`, which controls whether debug messages emit in debug builds. The macros for `rtw_info`, `rtw_warn`, and `rtw_err` do not add state; they route messages to `rtwdev->dev`.

## Dependencies and Integration Points

`debug.h` is included broadly by driver subsystems that need categorized debug logging. It depends on the caller having visible `struct rtw_dev` and, for debugfs simple PHY information, `struct seq_file`. It integrates with Kconfig so debugfs and dynamic debug logging can be compiled out without changing call sites.

## Risks

The main risk is category misuse: excessive logging under hot paths can affect performance when debug masks are enabled, while using the wrong mask makes targeted diagnostics harder. Because disabled `rtw_dbg()` arguments are still type-checked but not evaluated in the inline stub, side-effectful arguments should be avoided.

## Test Signals

Build coverage should include debugfs/debug enabled and disabled combinations. Runtime checks should confirm category-specific logs appear only when `rtw_debug_mask` includes the category, while `rtw_info/warn/err` remain available regardless of config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/efuse.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/efuse.c

## Purpose

`efuse.c` reads Realtek physical eFuse storage, reconstructs the logical eFuse map, and passes that logical map to chip-specific parsing code. eFuse data is the device's nonvolatile configuration source for MAC address, RF front-end information, regulatory/power characteristics, and hardware capability fields used during probe and bring-up.

## Important APIs, Types, and Functions

`rtw_parse_efuse_map()` is the main entry point. It allocates physical and logical maps using sizes already stored in `rtwdev->efuse`, dumps physical eFuse, reconstructs logical eFuse contents, then calls `chip->ops->read_efuse(rtwdev, log_map)` for chip-specific interpretation.

`rtw_read8_physical_efuse()` is exported for single-byte physical reads. It programs the address field in `REG_EFUSE_CTRL`, clears `BIT_EF_FLAG`, polls until the flag is set, and returns either the low data byte or `EFUSE_READ_FAIL` on timeout.

Internal helpers include `switch_efuse_bank()`, `rtw_dump_physical_efuse_map()`, and `rtw_dump_logical_efuse_map()`. The logical parser uses the local header macros to recognize 1-byte and 2-byte eFuse headers, block indexes, word-enable bits, and logical byte offsets.

## Control Flow

Physical dump flow first grants eFuse ownership through `rtw_chip_efuse_grant_on()`, selects the Wi-Fi eFuse bank, disables the chip 2.5V LDO through `chip->ops->cfg_ldo25(false)`, and loops over every physical byte. Each iteration writes the target address and a cleared flag into `REG_EFUSE_CTRL`, waits up to 1,000,000 microsecond-delay iterations for `BIT_EF_FLAG`, and stores the returned data byte. On success it releases the grant with `rtw_chip_efuse_grant_off()`.

Logical reconstruction walks physical bytes until the protected tail region or an invalid header. A 2-byte header is identified when the low five bits of the first header are `0xf`; otherwise a compact 1-byte header is used. For each enabled word, the parser copies two physical bytes into the logical map at `block_idx * 8 + word * 2`, validating both physical and logical bounds. The logical map is initialized to `0xff`, preserving unwritten eFuse semantics.

## State and Persistence

The eFuse itself is persistent hardware storage, but this file only reads it. Parsed values persist afterward in `rtwdev->efuse` and other fields populated by the chip-specific `read_efuse` operation. Temporary physical and logical maps are freed before return. The code changes transient hardware state by selecting the Wi-Fi bank, toggling eFuse grant, and disabling the 2.5V LDO during physical reads.

## Dependencies and Integration Points

This file depends on register definitions in `reg.h`, MMIO helpers from `hci.h`, chip operations for eFuse grant/LDO control/chip-specific parsing, and the size fields in `struct rtw_efuse`. It integrates early in device initialization, before many capability-dependent decisions in MAC, PHY, firmware, and regulatory paths.

## Risks

The physical dump has an important cleanup risk: if polling times out inside `rtw_dump_physical_efuse_map()`, the function returns `-EBUSY` before the final grant-off call. That can leave eFuse ownership state uncleared depending on lower-layer behavior. The parser also depends on correct `physical_size`, `protect_size`, and `logical_size`; bad values can reject maps or truncate valid data. Header handling treats `0xff` and selected extended-header forms as end-of-map, so corrupted physical eFuse can silently produce a mostly `0xff` logical map until chip parsing fails or yields defaults.

## Test Signals

Probe tests should confirm `rtw_parse_efuse_map()` succeeds on supported chips and logs failures for malformed maps. Unit-style parser tests can feed synthetic physical maps covering 1-byte headers, 2-byte headers, skipped words, invalid headers, logical overflow, and protected-tail boundaries. Hardware tests should verify eFuse grant is released after successful reads, single-byte reads return expected values, and chip-specific capability fields match known board data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/efuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/efuse.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/efuse.h

## Purpose

`efuse.h` declares the public eFuse read interface and bitfield helpers for extracting hardware capability values from the logical eFuse map. It is the shared contract between generic eFuse dumping and chip-specific eFuse parsers.

## Important APIs, Types, and Functions

The file defines hardware capability constants such as `EFUSE_HW_CAP_PTCL_VHT`, supported bandwidth bit positions, and `EFUSE_READ_FAIL`. The `GET_EFUSE_HW_CAP_*` macros extract HCI type, bandwidth support, NSS, antenna number, and protocol fields from a little-endian capability blob using `le32_get_bits()`.

It declares `rtw_parse_efuse_map()` and exported `rtw_read8_physical_efuse()`.

## Control Flow

The header has no runtime flow. It supplies macros used by parsers after `efuse.c` reconstructs the logical eFuse map.

## State and Persistence

The macros read caller-provided eFuse buffers and do not mutate state. The declarations refer to functions that populate persistent `rtwdev->efuse` state during initialization.

## Dependencies and Integration Points

Consumers must pass correctly aligned and sufficiently large hardware capability buffers because the macros cast to `__le32 *` and index word 1. The header integrates with chip-specific `read_efuse` implementations, HCI selection, PHY capability setup, and feature advertisement.

## Risks

The capability macros assume the buffer layout is valid for the target chip. Using them on a shorter or differently formatted map can read the wrong word and misconfigure HCI, NSS, antennas, or protocol capabilities. Any new chip family with a different eFuse capability layout needs separate parsing rather than blindly reusing these helpers.

## Test Signals

Tests should compare parsed HCI/BW/NSS/antenna/protocol values against known eFuse dumps for each chip family. Build tests should cover endian helpers and ensure all users include the required bitops/endian definitions through their include chain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/efuse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/fw.c

## Purpose

`fw.c` is the main firmware communication and firmware-offload implementation for `rtw88`. It handles C2H receive dispatch, H2C mailbox and packet commands, firmware debug dumping, rate-adaptation reports, beacon-filter notifications, coexistence commands, power-save/WoWLAN commands, reserved-page construction and download, firmware FIFO dumps, probe-request updates, scan offload, and scan channel-switch notifications.

## Important APIs, Types, and Functions

Public entry points include `rtw_fw_c2h_cmd_rx_irqsafe()`, `rtw_fw_c2h_cmd_handle()`, `rtw_fw_c2h_cmd_isr()`, `rtw_fw_send_general_info()`, `rtw_fw_send_phydm_info()`, `rtw_fw_do_iqk()`, `rtw_fw_inform_rfk_status()`, coexistence H2C helpers, `rtw_fw_send_rssi_info()`, `rtw_fw_send_ra_info()`, `rtw_fw_media_status_report()`, `rtw_fw_beacon_filter_config()`, WoW/LPS/NLO command helpers, reserved-page add/remove/download helpers, `rtw_fw_dump_fifo()`, `rtw_fw_update_pkt_probe_req()`, `rtw_fw_channel_switch()`, `rtw_fw_adaptivity()`, scan notify/offload helpers, and operating-channel backup/restore helpers.

The implementation revolves around protocol structures and macros from `fw.h`: `struct rtw_c2h_cmd`, `struct rtw_c2h_ra_rpt`, `struct rtw_h2c_cmd`, `struct rtw_rsvd_page`, reserved packet types, H2C command IDs, H2C packet subcommands, and field setters for little-endian firmware buffers.

## Control Flow

C2H handling has an IRQ-safe front half and a mutex-protected worker path. `rtw_fw_c2h_cmd_rx_irqsafe()` stores the packet offset in `skb->cb`, immediately handles BT MP responses, WLAN RF-on completion, and scan-density reports, and queues all other events to `rtwdev->c2h_queue` plus `c2h_work`. `rtw_fw_c2h_cmd_handle()` locks `rtwdev->mutex`, ignores events while the device is not running, and dispatches by C2H ID to TX reports, coexistence notifications, beacon-filter notifications, HALMAC extensions, RA reports, and adaptivity diagnostics.

H2C command flow supports two transports. Short register/mailbox commands use `rtw_fw_send_h2c_command()` or `rtw_fw_send_h2c_command_register()`, polling `REG_HMETFR` for a free mailbox, writing the extended word first, then the command word, and rotating `rtwdev->h2c.last_box_num`. Packet H2C commands use `rtw_fw_send_h2c_packet()`, stamp `rtwdev->h2c.seq`, and call `rtw_hci_write_data_h2c()`.

Reserved-page flow starts with per-vif lists created by `rtw_add_rsvd_page_bcn()`, `rtw_add_rsvd_page_sta()`, or `rtw_add_rsvd_page_pno()`. `rtw_fw_download_rsvd_page()` gathers active vif entries into the device build list, ensures the first page is a beacon or dummy page, creates skb contents through mac80211 helpers or local builders, optionally prepends TX descriptors, lays packets into page-aligned firmware buffer space, downloads the buffer through `rtw_fw_write_data_rsvd_page()`, then downloads the beacon alone again so the beacon's TX descriptor is correct.

Scan offload flow uses reserved H2C information pages. `rtw_hw_scan_start()` stops queues, leaves deep LPS, flushes queues, configures randomized or normal scan address state, and disables beacon BSSID filtering. `rtw_hw_scan_offload()` builds probe requests and channel lists, writes them to reserved pages, then sends an H2C scan-offload packet. Firmware C2H channel-switch notifications update the driver's current channel, stop or wake queues around off-channel work, notify coexistence of 2.4/5 GHz transitions, and manage beaconing. Scan status C2H completes the scan and reports abort status to mac80211.

## State and Persistence

Persistent driver state updated here includes `rtwdev->h2c.last_box_num`, `rtwdev->h2c.seq`, station RA report fields and AMSDU limits, `rtwdev->beacon_loss`, `dm_info->tx_rate`, `dm_info->scan_density`, LPS/WoW command-derived flags, reserved-page build locations, `rsvd_pkt->page`, `rsvd_pkt->tim_offset`, `rsvd_pkt->probe_req_size`, `rtwdev->scan_info` operating-channel fields, and temporary probe-page size. Firmware receives persistent command state for RA masks, RSSI, media status, beacon filtering, power mode, WoWLAN, NLO, packet locations, and scan offload.

Most H2C and reserved-page paths require `rtwdev->mutex`; several functions assert it. The C2H front half is designed for IRQ-safe contexts and defers most work. Reserved-page build lists are temporary and reset before each build, while per-vif reserved-page lists persist until interface removal.

## Dependencies and Integration Points

`fw.c` integrates with mac80211 skb constructors (`ieee80211_beacon_get_tim`, `ieee80211_pspoll_get`, `ieee80211_nullfunc_get`, `ieee80211_probereq_get`), HCI data paths, TX descriptor filling, security CAM backup, coexistence notification handling, power-save and WoW helpers, PHY/SAR/adaptivity state, firmware recovery, and core scan state. It is called from mac80211 callbacks in `mac80211.c`, MAC bring-up in `mac.c`, debugfs H2C and FIFO dump paths, and power-management paths.

## Risks

Firmware protocol packing is brittle. Every H2C field setter assumes the exact firmware ABI, little-endian layout, and packet length. A wrong bitfield, stale feature gate, or missing sequence update can silently break offloaded behavior. The code also has many hardware sequencing assumptions: mailbox free polling, reserved-page register backup/restore, beacon-valid polling, RX clock-gate toggling during FIFO dump, and queue stops around scan channel switches.

Reserved-page construction is size-sensitive. The first packet rule, page-margin math, chip page size, TX descriptor size, and reserved driver page count must all align. Oversized probe requests or too many PNO/scan entries fail, and errors during build must free all temporary skbs. `rtw_fw_dump_check_size()` appears weak for TX/RX FIFO bounds because it compares `start_addr + size` with a base page address rather than a FIFO length, so callers still need conservative inputs.

Concurrency risks center on firmware events racing stop/restart/scanning. The worker path drops C2H while not running, scan abort and completion share `scan_info.scanning_vif`, and debugfs can inject H2C commands outside normal typed call sites.

## Test Signals

Validation should cover C2H dispatch for RA reports, TX reports, BT/coex info, beacon loss/signal events, scan density, scan status, and channel switch notifications. H2C tests should verify mailbox rotation, timeout logging, packet sequence increments, and feature-gated commands on firmware versions with and without beacon filter or scan offload. Reserved-page tests should exercise station, AP, PNO, LPS page, and beacon update paths, including page overflow and skb allocation failures. Hardware scan tests should cover active/passive/radar channels, randomized addresses, AP-active beacon preservation, aborts, firmware error codes, and queue stop/wake behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/fw.h

## Purpose

`fw.h` is the firmware protocol contract for `rtw88`. It defines H2C and C2H command IDs, packet sizes, firmware header layouts, firmware feature bits, reserved-page packet types, WoWLAN/NLO/scan data structures, firmware bitfield pack/unpack macros, feature-check helpers, and prototypes for all firmware interaction routines implemented in `fw.c`.

## Important APIs, Types, and Functions

Key C2H protocol types are `enum rtw_c2h_cmd_id`, `enum rtw_c2h_cmd_id_ext`, `struct rtw_c2h_cmd`, `struct rtw_c2h_adaptivity`, and `struct rtw_c2h_ra_rpt`. Key H2C command types include `struct rtw_h2c_register`, `struct rtw_h2c_cmd`, H2C packet subcommand constants, and command ID constants for media status, power mode, RA, RSSI, beacon filtering, scan, adaptivity, coexistence, WoWLAN, AOAC, NLO, and BT recovery.

Firmware image metadata is represented by `struct rtw_fw_hdr` for newer firmware and `struct rtw_fw_hdr_legacy` for legacy 8051 firmware. `enum rtw_fw_feature` and `enum rtw_fw_feature_ext` gate optional firmware behavior such as LPS C2H, low clock, page features, beacon filter, scan notification, adaptivity, scan offload, and old probe-page numbering.

Reserved/offload data structures include `struct rtw_rsvd_page`, `struct rtw_lps_pg_dpk_hdr`, `struct rtw_lps_pg_info_hdr`, `struct rtw_nlo_info_hdr`, `struct rtw_ch_switch_option`, and enums for reserved packet type, keepalive type, scan channel type, scan report code, and scan notify IDs.

## Control Flow

The header itself has no runtime flow, but it shapes all firmware flow. `rtw_h2c_pkt_set_header()` fills the common packet-H2C category, command ID, and subcommand fields. Inline feature checks test bitmasks stored in `struct rtw_fw_state`. `get_c2h_from_skb()` interprets the packet offset stored in `skb->cb`, which is set by the IRQ-safe C2H receive path.

The many `SET_*` macros encode fields into command buffers through `le32p_replace_bits()` or `u8p_replace_bits()`. The `GET_*` macros decode C2H payloads and firmware dump TLVs.

## State and Persistence

The types defined here describe state persisted elsewhere: firmware feature masks in `rtwdev->fw`, reserved page list entries in vifs and device build lists, firmware sequence counters in `rtwdev->h2c`, WoW and PNO settings in `rtwdev->wow`, and scan offload state in `rtwdev->scan_info`. Packed headers are written into firmware-owned memory or parsed from firmware-owned messages.

## Dependencies and Integration Points

`fw.h` is included by MAC setup, debugfs, power-save, WoWLAN, coexistence, scan, TX report, and mac80211 integration code. It depends on Linux endian and bitfield helpers and on driver types declared in `main.h` and related headers. Because the macros operate on raw byte buffers, callers must zero-initialize H2C packets, set total lengths consistently, and hold required locks before sending.

## Risks

The primary risk is ABI drift. A field location mismatch between these macros and firmware will break behavior while still compiling. Several macros cast arbitrary `u8 *` buffers to `__le32 *`, so callers must provide properly sized, suitably aligned buffers and account for little-endian layout. Structure packing must match firmware exactly; removing `__packed` or changing field sizes would corrupt messages. Feature checks must be respected before using optional firmware commands.

## Test Signals

Build tests should catch prototype drift between `fw.h` and `fw.c`. Runtime tests should verify firmware version parsing, feature-bit gating, H2C byte streams for representative commands, C2H payload decoding, reserved-page location reporting, scan offload command layout, and WoW/NLO command layout against known-good firmware traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/hci.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/hci.h

## Purpose

`hci.h` defines the host-controller-interface abstraction used by the generic `rtw88` core to run over PCIe, USB, and SDIO. It hides bus-specific TX, firmware download, reserved-page writes, H2C writes, power-save signaling, queue flushing, and register access behind `struct rtw_hci_ops` plus inline wrappers.

## Important APIs, Types, and Functions

`struct rtw_hci_ops` contains function pointers for packet TX, TX kickoff, queue flush, setup/start/stop, deep and link power-save entry, interface configuration, optional dynamic RX aggregation, firmware page writes, reserved-page writes, H2C data writes, and 8/16/32-bit MMIO-like register access.

Inline wrappers such as `rtw_hci_tx_write()`, `rtw_hci_setup()`, `rtw_hci_start()`, `rtw_hci_stop()`, `rtw_hci_write_data_h2c()`, `rtw_read8/16/32()`, and `rtw_write8/16/32()` centralize the calls. Helper wrappers provide set/clear operations, masked reads/writes, RF register access through chip ops, HCI type lookup, and optional queue flushing.

## Control Flow

Most wrappers directly dispatch into `rtwdev->hci.ops`. Optional operations such as `dynamic_rx_agg` and `flush_queues` are guarded by null checks. RF read/write wrappers assert that `rtwdev->mutex` is held before calling chip-specific RF operations. Masked writes perform read-modify-write operations and `rtw_write32_mask()` warns on unaligned 32-bit addresses.

## State and Persistence

This header does not own state. It routes operations through `rtwdev->hci`, whose `type`, `ops`, bus-specific parameters, and power-management addresses are initialized by the bus driver. Register writes and RF writes persist in hardware; queue flushes and power-save operations affect bus/device runtime state.

## Dependencies and Integration Points

Every file in this subset depends on `hci.h` either directly or indirectly for register access. It integrates the generic core with PCIe, USB, and SDIO modules, chip RF operations, firmware download paths in `mac.c`, H2C/reserved-page writes in `fw.c`, debugfs raw register access in `debug.c`, and MAC queue flushing.

## Risks

Because these wrappers are thin, invalid or missing HCI ops will crash or misbehave at call sites. Read-modify-write helpers are not atomic with respect to other hardware writers unless the caller holds the appropriate lock. Masked helpers assume nonzero masks because they call `__ffs(mask)`. RF helpers require the mutex; violating that contract should trip lockdep and can race PHY/RF state.

## Test Signals

Bus-specific tests should verify each HCI implementation fills all mandatory ops and that generic bring-up works over PCIe, USB, and SDIO. Lockdep should be enabled to catch RF access without `rtwdev->mutex`. Register mask tests should verify set/clear/read/write helpers preserve unrelated bits and handle byte/word/dword widths correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/hci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/led.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/led.c

## Purpose

`led.c` provides optional Linux LED class integration for `rtw88`. When a chip supplies a `led_set` operation and `CONFIG_RTW88_LEDS` is enabled, it registers a device LED named from the Realtek device and attaches mac80211's throughput trigger so LED blink rate tracks radio traffic.

## Important APIs, Types, and Functions

`rtw_led_init()` initializes `rtwdev->led_cdev`, assigns `brightness_set_blocking`, fills a stable LED name, creates a throughput LED trigger with `ieee80211_create_tpt_led_trigger()`, and registers the LED class device. `rtw_led_deinit()` turns the LED off through the chip operation and unregisters it if registration succeeded. The internal `rtw_led_set()` callback maps LED brightness changes to `rtwdev->chip->ops->led_set()` under `rtwdev->mutex`.

## Control Flow

Initialization exits early when the chip has no LED operation. Otherwise it builds a static throughput-to-blink-time table, configures the LED classdev, registers it, and records `rtwdev->led_registered` only on success. Runtime brightness changes are serialized by the device mutex. Deinit checks `led_registered`, forces `LED_OFF`, then unregisters.

## State and Persistence

LED state lives in `rtwdev->led_cdev`, `rtwdev->led_name`, and `rtwdev->led_registered`. Hardware LED state persists until changed by the chip `led_set` operation; deinit explicitly turns it off.

## Dependencies and Integration Points

This file depends on Linux LED classdev support, mac80211 throughput LED triggers, the chip-specific `led_set` callback, and driver logging. It integrates with device initialization and teardown through the prototypes in `led.h`.

## Risks

The chip `led_set` callback is called with the driver mutex held; chip implementations must not take locks in an order that deadlocks with other driver paths. `rtw_led_deinit()` calls `chip->ops->led_set()` without checking the callback again, relying on `led_registered` only being true when the callback existed at init. Registration failures leave LED integration disabled but should not block device operation.

## Test Signals

Tests should cover chips with and without `led_set`, LED class registration failure handling, throughput-trigger name creation, brightness changes under traffic, suspend/remove deinit turning the LED off, and lockdep behavior in chip LED callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/led.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/led.h

## Purpose

`led.h` declares the optional LED integration API for `rtw88` and provides no-op stubs when LED support is disabled.

## Important APIs, Types, and Functions

With `CONFIG_RTW88_LEDS`, it declares `rtw_led_init()` and `rtw_led_deinit()`. Without that config, both functions are static inline empty functions so callers can invoke them unconditionally.

## Control Flow

There is no runtime flow in the header other than compile-time Kconfig selection between real functions and stubs.

## State and Persistence

No state is owned by the header. Real LED state is stored in `struct rtw_dev` fields used by `led.c`.

## Dependencies and Integration Points

The header is included by core initialization and teardown code that should not need to know whether LED support is compiled in. It depends on `struct rtw_dev` being declared by included driver headers.

## Risks

The main risk is build coverage: both LED-enabled and LED-disabled configurations need to compile. Callers should not assume LED side effects occur when the config is disabled or the chip lacks `led_set`.

## Test Signals

Compile tests should cover `CONFIG_RTW88_LEDS=y` and disabled builds. Runtime tests should verify init/deinit calls are harmless on chips without LEDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/led.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/mac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/mac.c

## Purpose

`mac.c` implements low-level MAC and firmware bring-up for `rtw88`. It programs channel-related MAC registers, parses chip power sequences, powers the MAC on and off, downloads firmware through either modern DDMA/reserved-page flow or legacy page writes, configures TX/RX FIFO page layout, maps software queues to hardware priority queues, initializes H2C packet queue state, configures RX driver-info reporting, and runs chip-specific MAC init/postinit hooks.

## Important APIs, Types, and Functions

Public APIs include `rtw_set_channel_mac()`, `rtw_pwr_seq_parser()`, `rtw_mac_power_on()`, `rtw_mac_power_off()`, `rtw_write_firmware_page()`, `rtw_download_firmware()`, `rtw_mac_flush_queues()`, `rtw_set_trx_fifo_info()`, `rtw_ddma_to_fw_fifo()`, `rtw_mac_init()`, and `rtw_mac_postinit()`.

Important internal helpers are `rtw_mac_pre_system_cfg()`, `rtw_mac_power_switch()`, system-config variants for modern and legacy WCPU, firmware size validation, WLAN CPU enable/disable, firmware-download register backup/restore, DDMA setup/checksum helpers, modern and legacy firmware download validators, priority queue configuration, TXDMA queue mapping, H2C queue initialization, and RX driver-info configuration.

## Control Flow

Power-on flow starts in `rtw_mac_power_on()`. It runs pre-system bus and pinmux setup, switches power on using the chip's power-on sequence, handles an already-on MAC by power-cycling and retrying, then initializes system registers using legacy or modern WCPU paths. Power-off delegates to `rtw_mac_power_switch(false)`. Power sequence parsing selects an interface mask from the active HCI type and a cut-version mask from `hal.cut_version`, then executes write, polling, delay, and read commands from chip tables.

Modern firmware download first checks the Realtek firmware header sizes, optionally backs up LTE coexistence state, disables the WLAN CPU, backs up and reprograms TX queue/beacon registers for firmware download, resets the platform, copies DMEM/IMEM/optional EMEM sections through TX buffer plus DDMA into firmware memory, verifies checksums, restores registers, marks firmware download ready, re-enables the CPU, restores LTE coexistence state, validates firmware readiness, resets HCI descriptors, clears H2C counters, and sets `RTW_FLAG_FW_RUNNING`. Legacy firmware download enables legacy firmware-download mode, writes 4 KiB pages through `rtw_hci_write_firmware_page()`, validates report bits, restarts the CPU, and then performs the same HCI/H2C flag reset.

MAC init flow is `rtw_mac_init()`: queue mapping, priority/FIFO page setup, H2C queue setup, chip-specific `mac_init`, RX driver-info configuration, and bus interface config. `rtw_mac_postinit()` calls the optional chip postinit hook. Queue flushing maps mac80211 AC queues through `rtwdev->fifo.rqpn` to hardware priority queues, then polls reserved and available page counts for up to about 100 ms per priority.

## State and Persistence

Persistent driver state updated here includes `RTW_FLAG_POWERON`, `RTW_FLAG_FW_RUNNING`, `rtwdev->fifo` page counts and reserved addresses, `rtwdev->fifo.rqpn`, `rtwdev->h2c.last_box_num`, `rtwdev->h2c.seq`, and MAC/RX configuration registers. Firmware download temporarily backs up six registers and restores them after transfer. Queue setup persists page boundaries, queue maps, H2C queue base/tail pointers, RX FIFO boundaries, and LLT initialization in hardware.

## Dependencies and Integration Points

`mac.c` depends on chip tables and callbacks in `struct rtw_chip_info`, HCI operations for register access and firmware-page writes, firmware reserved-page writer from `fw.c`, SDIO helpers, LTE coexistence accessors, register definitions, and generic helpers such as `check_hw_ready()` and `rtw_restore_reg()`. Higher-level core start paths call power, firmware download, MAC init, and postinit in sequence.

## Risks

Bring-up ordering is fragile. Power sequence commands are chip/cut/interface-specific and poll hardware state; wrong masks or missing delays can leave the MAC half-powered. Modern firmware download relies on exact firmware section sizes and checksum markers; incorrect header parsing, DDMA source/destination addresses, or register restore failures can prevent firmware boot. Some failure paths after LTE coexistence backup or register backup may not restore every temporary state before returning.

FIFO and queue layout is another high-risk area. Reserved page counts must not exceed TX FIFO pages, and all derived addresses must line up with firmware expectations. Wrong page-table selection for USB bulkout count, PCIe, or SDIO breaks queue scheduling and firmware H2C placement. Queue flushing is best-effort and can time out under heavy traffic.

## Test Signals

Hardware bring-up tests should verify power-on/off across PCIe, USB, and SDIO chips, including already-on retry and SDIO resume polling. Firmware tests should cover modern and legacy images, bad size/checksum images, missing firmware-ready bits, 8821C PCIe BT recovery H2C, and HCI descriptor reset after download. FIFO tests should validate reserved boundaries, H2C queue free-space checks, page table selection by bus/bulkout count, and queue flush behavior under traffic. Channel tests should verify MAC bandwidth, subchannel, CCK check, and timing registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/mac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/mac.h

## Purpose

`mac.h` declares the low-level MAC, firmware download, queue, FIFO, and DDMA interfaces implemented by `mac.c`, and defines shared constants for MAC port count, firmware memory base addresses, reserved page accounting, and firmware download buffer sizing.

## Important APIs, Types, and Functions

The header defines `RTW_HW_PORT_NUM`, `cut_version_to_mask()`, polling and buffer constants, OCP base addresses for RX buffer, TX buffer, ROM, IMEM, DMEM, and EMEM, and reserved-page counts for driver pages, H2C extra/static info, H2C queue, CPU instruction space, and firmware TX buffer.

It declares channel MAC programming, power sequence parsing, MAC power on/off, firmware page write, firmware download, MAC init/postinit, MAC queue flush, TRX FIFO setup, and DDMA-to-firmware-FIFO transfer. It also provides `rtw_mac_flush_all_queues()` as a helper around `rtw_mac_flush_queues()`.

## Control Flow

The header has no runtime flow; callers use it to invoke the bring-up sequence implemented in `mac.c`. Typical order is power on, firmware download, MAC init, postinit, then runtime queue/channel operations.

## State and Persistence

The constants guide persistent hardware layout and firmware memory transfers. Functions declared here update `rtwdev` flags, FIFO state, H2C state, and hardware registers, but the header itself owns no state.

## Dependencies and Integration Points

`mac.h` is included by core, firmware, debug, and bus code that needs MAC bring-up or queue management. The OCP addresses and reserved page counts must match firmware expectations and chip information tables.

## Risks

Changing shared constants can break firmware download, reserved-page placement, or H2C queue placement across all chips. `cut_version_to_mask()` assumes cut values map cleanly to `1 << (cut + 1)`; new cut encodings would require review.

## Test Signals

Compile tests should catch declaration drift. Runtime tests for all supported buses should verify firmware download addresses, reserved-page boundaries, MAC queue flushing, and channel programming still match hardware expectations after any changes to these constants or prototypes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/mac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/mac80211.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/mac80211.c

## Purpose

`mac80211.c` exposes `rtw88` to the Linux mac80211 subsystem through `const struct ieee80211_ops rtw_ops`. It translates mac80211 lifecycle, interface, BSS, key, station, aggregation, scan, power-management, antenna, SAR, and TX-queue callbacks into Realtek core, MAC, firmware, security, coexistence, beamforming, WoWLAN, and PHY operations.

## Important APIs, Types, and Functions

The exported object is `rtw_ops`. Important callbacks include `rtw_ops_tx()`, `rtw_ops_wake_tx_queue()`, `rtw_ops_start()`, `rtw_ops_stop()`, `rtw_ops_config()`, interface add/remove/change, filter configuration, BSS info changes, AP start/stop, TX queue parameter configuration, station add/remove, TIM updates, key setup/removal, AMPDU action, AMSDU policy, software and hardware scan operations, managed TX preparation, RTS threshold, station statistics, flush, bitrate mask, antenna get/set, suspend/resume/set_wakeup under `CONFIG_PM`, restart reconfig completion, SAR specs, and station RC update.

`rtw_vif_port[]` maps up to five hardware ports to MAC address, BSSID, network type, AID, and beacon-control registers. Helpers convert EDCA parameters, configure all ACs, and update station RA masks when bitrate masks change.

## Control Flow

Start/stop are simple mutex-protected calls to `rtw_core_start()` and `rtw_core_stop()`. Config changes cancel pending IPS work, leave deep LPS, leave idle power save when waking, set channel on channel changes, and enter IPS when becoming idle outside scan.

Interface add allocates a MAC ID and hardware port, initializes TXQ and reserved-page lists, selects network type and beacon-control defaults by interface type, adds the appropriate reserved pages, writes port configuration, switches core port, and recalculates LPS. Interface removal leaves deep LPS, cleans TXQ and reserved pages, clears port registers, releases the hardware port and MAC ID, and recalculates LPS.

BSS changes drive connection state. On association, the driver updates vif association state, notifies coexistence, downloads reserved pages, sends reserved-page H2C, sets default port, sends media status, optionally configures beamforming, AMPDU factor, and beacon filter. On disassociation it leaves LPS, tears down beamforming, and aborts an ongoing firmware scan if needed. Beacon changes refresh DTIM/reserved pages; beacon enable toggles beacon queue download; CQM changes update firmware beacon filter; ERP slot changes reprogram EDCA.

Security flow maps supported cipher suites to hardware CAM types, chooses CAM entries, sets IV/MMIC/SW management TX flags as needed, writes or clears CAM entries, flushes queues before clearing keys, and refreshes reserved pages when deep LPS page backup is active. Unsupported modern ciphers return `-EOPNOTSUPP` or `-ENOTSUPP`.

Scan flow supports both software scan callbacks and firmware scan offload. Hardware scan checks firmware feature support, rejects concurrent scans, starts scan state, builds offload data via `fw.c`, and aborts/cleans up on failure or cancellation. PM callbacks delegate to WoW suspend/resume and device wakeup configuration.

## State and Persistence

This file mutates much of the driver's high-level runtime state: `rtwdev->flags`, vif MAC IDs and ports, `rtwvif->net_type`, BSSID, beacon control, TX parameters, reserved-page lists, scan request pointers, AP-active flag, operating-channel backup, hardware RX filter bits in `hal.rcr`, security CAM allocation, station RA masks, TXQ AMPDU flags, RTS threshold, and LED/firmware-visible state indirectly through lower layers.

Most callbacks take `rtwdev->mutex` before touching shared hardware or driver state. TXQ scheduling uses `rtwdev->txq_lock` and the TX workqueue. Some callbacks intentionally leave LPS/deep LPS before changing hardware state to avoid firmware or power-save races.

## Dependencies and Integration Points

`mac80211.c` is the integration point between Linux networking and the rest of `rtw88`. It calls core start/stop/channel/scan helpers, firmware reserved-page and scan-offload helpers, security CAM helpers, TX scheduling, MAC queue flushes, HCI flushes, coexistence notifications, power-save transitions, beamforming, WoWLAN, SAR, PHY calibration, antenna callbacks, and station-rate update work.

## Risks

Lifecycle error handling needs care. In `rtw_ops_add_interface()`, if MAC ID acquisition succeeds but no hardware port is available, the function returns without releasing the MAC ID, which can leak MAC ID allocation on that failure path. The unsupported interface-type path clears the port but also does not visibly release the acquired MAC ID. These paths may be rare but are testable with port exhaustion or unsupported interface types.

Connection and scan flows are race-sensitive. Disassociation can abort scans, hardware scan completion uses `scan_info.scanning_vif`, AP-active scan paths temporarily stop beaconing and queues, and many operations leave LPS before touching hardware. Key removal flushes both HCI and MAC queues but still depends on no new packets using a CAM entry after clearing. EDCA calculations depend on current band and slot-time state.

## Test Signals

Mac80211 integration tests should cover interface add/remove/change across station, AP, mesh, and adhoc; port exhaustion; MAC ID leak checks; association/disassociation reserved-page and beacon-filter behavior; AP start/stop; key install/remove for WEP/TKIP/CCMP and unsupported ciphers; AMPDU transitions; bitrate masks; antenna get/set; RTS threshold; scan start/cancel/completion for software and firmware offload; WoW suspend/resume; SAR update; and restart reconfiguration clearing `RTW_FLAG_RESTARTING`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/mac80211.c -->
