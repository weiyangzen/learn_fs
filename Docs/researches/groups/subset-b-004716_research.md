# Research Report: subset-b-004716

Work item `subset-b-004716` covers ath10k core lifecycle, shared state, firmware coredump, and debugfs support files under `sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/core.c

## Purpose

`core.c` is the central lifecycle implementation for the Qualcomm Atheros ath10k 802.11ac driver. It binds bus-specific HIF implementations to common firmware loading, board/calibration selection, WMI/HTT/HTC bring-up, mac80211 registration, crash recovery, debugfs/coredump registration, and teardown. It also defines module parameters (`debug_mask`, `cryptmode`, `uart_print`, `skip_otp`, `frame_mode`, `coredump_mask`, `fw_diag_log`) that materially change boot, crypto, logging, datapath framing, and crash-dump behavior.

## Important APIs, Data, and Functions

The static `ath10k_hw_params_list[]` is the hardware capability table for supported devices and buses. Entries select firmware directories, board sizes, patch addresses, hardware ops, RX descriptor ops, cipher suite counts, target layout flags, peer/stat capabilities, diagnostic CE download support, raw-mode constraints, and restart behavior. `ath10k_init_hw_params()` resolves this table by bus, target version, and device id; a mismatch fails probing.

Firmware and board APIs are centered on `ath10k_fetch_fw_file()`, `ath10k_core_fetch_firmware_files()`, `ath10k_core_fetch_firmware_api_n()`, `ath10k_core_fetch_board_file()`, `ath10k_core_fetch_board_data_api_n()`, and `ath10k_core_fetch_board_data_api_1()`. Firmware API parsing validates `ATH10K-FW` magic, walks information elements, and stores pointers to firmware image, OTP image, code-swap data, WMI/HTT op versions, version string, and feature bits. Board API 2 parsing validates board magic and looks up generated board names with variant and fallback names; API 1 falls back to legacy board files.

Calibration and OTP flow uses `ath10k_download_cal_data()` and helpers for nvmem, firmware files, Device Tree properties, target EEPROM, and OTP. `ath10k_core_get_board_id_from_otp()` and `ath10k_core_get_ext_board_id_from_otp()` execute OTP payloads through BMI to discover board ids. `ath10k_core_check_smbios()` and `ath10k_core_check_dt()` populate BDF variants from SMBIOS or Device Tree.

The main lifecycle entry points exported to bus drivers and mac layers are `ath10k_core_create()`, `ath10k_core_register()`, `ath10k_core_start()`, `ath10k_core_stop()`, `ath10k_core_start_recovery()`, `ath10k_core_unregister()`, and `ath10k_core_destroy()`.

## Control Flow

Creation allocates the mac80211 object through `ath10k_mac_create()`, installs hardware register/value tables by `hw_rev`, initializes completions, locks, waitqueues, skb queues, work items, workqueues, NAPI dummy device, coredump storage, and debug storage. Registration is asynchronous: `ath10k_core_register()` stores bus parameters then queues `ath10k_core_register_work()`.

`ath10k_core_register_work()` enables peer stats, probes firmware, registers mac80211, coredump, debugfs, spectral, thermal, and LEDs, then marks `ATH10K_FLAG_CORE_REGISTERED`. Probe powers up HIF, gets target info through bus-specific BMI/HIF calls, initializes hardware parameters, fetches firmware and board data, initializes firmware feature-derived limits, starts firmware once to discover capabilities, prints boot information, stops firmware, and powers down.

`ath10k_core_start()` is the real boot path. For BMI firmware it starts BMI, optionally enables PLL, configures host-interest fields, downloads calibration/board data, handles skip-clock-init, downloads firmware, configures UART and SDIO target flags, then initializes HTC. It completes BMI, attaches WMI and HTT, allocates HTT TX/RX resources, starts HIF, waits for HTC, connects HTT/WMI, starts HTC, waits for WMI service/unified readiness, applies compatibility service bits, sets base MAC, optionally performs dummy-vdev RX-filter reset, refills RX ring, initializes vdev map/list state, sets up HTT, starts debug, target logging, and LEDs.

Stop reverses active runtime pieces: debug stop, optional target suspend, HIF stop, HTT TX stop/RX free, WMI detach, and BMI id invalidation. Unregister cancels register work, unregisters LEDs/thermal/spectral/mac80211/testmode, releases firmware and board files, and unregisters debugfs. Destroy frees workqueues, netdev, debug, coredump, HTT TX, WMI host memory, and mac object.

Recovery is workqueue-based. `ath10k_core_start_recovery()` queues `recovery_check_work` on an auxiliary queue. The check work guards against repeated failures, waits for overlapping recovery if needed, increments pending recovery, then queues `restart_work`. `ath10k_core_restart()` wakes/flushes waiters, drains TX, cancels coverage work, moves ON devices to RESTARTING, halts, finishes scan, asks mac80211 to restart hardware, and submits a devcoredump after unlocking.

## State and Persistence

Runtime state lives in `struct ath10k`: firmware components, `running_fw`, hardware params, WMI/HTT/HTC subobjects, locks, completions, workqueues, calibration mode, board ids, feature flags, vdev maps, peer state, debug state, coredump state, and counters. Persistent user-visible inputs are kernel module parameters, firmware files under linux-firmware paths, optional board/calibration files, nvmem cells, Device Tree properties, and SMBIOS BDF extension records. The file stores no disk data itself; it obtains firmware blobs through the kernel firmware API and releases them explicitly.

Concurrency contracts are strict: many exported lifecycle functions assert `conf_mutex` is held; crash dump storage uses `dump_mutex`; fast peer/stat structures use `data_lock`. Completions are used to break blocked scan, key, vdev, thermal, survey, and peer waiters during recovery.

## Dependencies and Integration Points

The file depends on HIF/BMI/HTC/WMI/HTT layers, mac80211, firmware loader, DMI, Device Tree, nvmem, PM QoS, LEDs, thermal, spectral, testmode, coredump, and debug modules. Firmware feature bits are consumed by WMI/HTT setup, raw mode, crypto mode, BT coexistence, IRAM recovery, service compatibility, and resource limits. Board/calibration decisions affect firmware boot correctness and regulatory/RF behavior.

## Risks

Boot logic has many fallback paths where a subtle ordering change can select the wrong board file or calibration source. API parsers must preserve alignment and length validation to avoid overreads on malformed firmware or board blobs. Recovery must avoid deadlocks with `conf_mutex`, work cancellation, and mac80211 restart callbacks. Module parameters such as software crypto/raw mode and coredump mask can change performance, memory footprint, and debug exposure. Error unwinding in `ath10k_core_start()` is asymmetric: some resources are freed in later stop/destroy paths, so changing a goto target can leak or double-free.

## Test Signals

Useful signals include successful firmware probe and mac80211 registration, printed hardware/firmware/board/boot info, expected board API selection, correct calibration mode, service-ready/unified-ready events, HTT connect and RX refill success, NAPI enable/disable behavior, simulated recovery via debugfs `simulate_fw_crash`, coredump submission on restart, and absence of lockdep warnings around `conf_mutex`, work cancellation, and NAPI synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/core.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/core.h

## Purpose

`core.h` defines the shared ath10k object model and public core API used by bus, MAC, HTT, WMI, debug, coredump, spectral, testmode, thermal, and WoW code. It is the driver-wide contract for firmware components, peers, stations, virtual interfaces, scan state, crash state, debug state, capabilities, locks, completions, and exported lifecycle functions.

## Important APIs, Types, and Constants

The header provides register bit helpers (`MS`, `SM`, `WO`), core timeouts, channel limits, RSSI/noise defaults, management pending limits, keepalive constants, BDF SMBIOS constants, recovery limits, and bus string mapping through `ath10k_bus_str()`.

SKB metadata is defined by `struct ath10k_skb_cb`, `struct ath10k_skb_rxcb`, and helpers `ATH10K_SKB_CB()`/`ATH10K_SKB_RXCB()`. These impose compile-time size checks against mac80211 SKB control storage and hold DMA addresses, endpoint ids, txq/vif pointers, flags, airtime estimate, and cipher metadata.

Major subsystem structures include `struct ath10k_wmi`, `struct ath10k_fw_stats`, `struct ath10k_tpc_stats`, `struct ath10k_peer`, `struct ath10k_sta`, `struct ath10k_vif`, `struct ath10k_fw_crash_data`, `struct ath10k_debug`, `struct ath10k_fw_file`, `struct ath10k_fw_components`, and `struct ath10k_bus_params`. `struct ath10k` itself aggregates all driver state and ends with aligned `drv_priv[]` for bus-private data.

The exported API prototypes cover NAPI control, object create/destroy, firmware feature string formatting, firmware API parsing, start/stop/suspend/recovery, registration/unregistration, board file fetching, Device Tree variant checking, and board file release.

## Control Flow and State Model

The header encodes a lifecycle state machine in `enum ath10k_state`: OFF, ON, RESTARTING, RESTARTED, WEDGED, and UTF. Comments document how recovery moves through RESTARTING/RESTARTED and why WEDGED blocks commands to avoid recursive recovery. `enum ath10k_firmware_mode` distinguishes normal 802.11 operation from UTF/factory test mode.

Firmware feature bits (`enum ath10k_fw_features`) are the central compatibility mechanism. They describe WMI dialects, raw mode, MFP, peer flow control, BT coexistence parameters, non-BMI loading, channel-info behavior, peer fixed rate, IRAM recovery, and several quirks. Device flags (`enum ath10k_dev_flags`) represent runtime conditions such as CAC, core registration, crash flush, raw mode, disabled hardware crypto, BT coexistence, peer stats, and NAPI enabled.

Per-peer and per-station state is split by locking. Peer keys, PN tracking, and peer maps are protected by `data_lock`. Station rate, retry, RX duration, power-save, TID config, and optional debugfs TID counters are stored in `struct ath10k_sta`. Per-vif state tracks vdev identity, beacon buffers, power save, AP/STA specific fields, WMM params, delayed connection-loss work, bitrate masks, and per-TID overrides.

## Persistence Behavior

The header itself persists nothing, but it names all in-memory state that mirrors persistent or externally supplied inputs: firmware metadata, board data pointers, calibration files, SMBIOS/Device Tree board variants, nvmem/EEPROM-derived calibration mode, runtime feature bits, and module-global `ath10k_frame_mode`/`ath10k_coredump_mask`. Firmware and board data pointers are owned by `struct firmware` objects managed in `core.c`.

## Dependencies and Integration Points

`core.h` includes Linux completion, PCI, UUID/time/LED facilities and ath10k subsystem headers (`htt.h`, `htc.h`, `hw.h`, `targaddrs.h`, `wmi.h`, DFS, spectral, thermal, wow, swap). Because nearly every ath10k translation unit includes it, changes here affect ABI-like internal contracts across bus drivers, mac80211 operations, debugfs, coredump collection, and firmware protocol parsing.

Conditional fields are important integration points. `CONFIG_ATH10K_DEBUGFS` embeds debug and spectral state; `CONFIG_DEV_COREDUMP` embeds coredump storage; `CONFIG_MAC80211_DEBUGFS` adds station TID stats; `CONFIG_ATH10K_DEBUG` changes debug logging behavior through declarations in `debug.h`.

## Risks

The largest risk is shared-state contract drift. Reordering or resizing SKB control blocks can violate mac80211 storage assumptions. Adding fields to `struct ath10k` without clear locking annotations can introduce races. Changing enum values can break firmware feature interpretation, debug masks, or user-space crash-dump ABI. Conditional compilation paths must keep inline stubs and real implementations behaviorally compatible. Because `struct ath10k_fw_crash_data` is written by bus crash handlers and packaged by coredump code, its locking and lifetime are cross-file sensitive.

## Test Signals

Compile-time `BUILD_BUG_ON` checks for SKB CB sizing and feature-string table size are key signals. Runtime signals include lockdep coverage for `conf_mutex`, `data_lock`, and `dump_mutex`; successful creation/destruction with all optional configs on/off; recovery transitions without stuck completions; debugfs builds with and without `CONFIG_ATH10K_DEBUGFS`; and devcoredump builds with and without `CONFIG_DEV_COREDUMP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/coredump.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/coredump.c

## Purpose

`coredump.c` implements ath10k firmware crash dump packaging for the Linux devcoredump facility. It maps supported hardware revisions to safe memory regions, sizes optional RAM dumps, allocates crash storage, builds the user-space dump file format, and submits dump buffers when recovery collects crash data.

## Important APIs, Data, and Functions

The file is dominated by static memory layout data. Register section arrays describe safe subranges for QCA6174 variants and IPQ4019/QCA4019 where some registers are intentionally skipped because they can reset state, require PCIe-active access, or cause bus hangs. Region arrays describe DRAM, AXI, IRAM, SRAM, IOREG, and MSA ranges for QCA6174, QCA9377, QCA988X, QCA99X0, QCA9984/QCA9888, QCA4019, and WCN3990. `hw_mem_layouts[]` binds hardware id, hardware revision, and bus to a region table.

`ath10k_coredump_get_mem_layout()` returns a layout only when the global `ath10k_coredump_mask` includes `ATH10K_FW_CRASH_DUMP_RAM_DATA`; `_ath10k_coredump_get_mem_layout()` bypasses the mask and is used by IRAM recovery code in `core.c`. `ath10k_coredump_get_ramdump_size()` sums all region lengths plus one `struct ath10k_dump_ram_data_hdr` per region and aligns the result to 16 bytes.

`ath10k_coredump_new()` initializes per-crash GUID and timestamp under `dump_mutex`. `ath10k_coredump_build()` creates the devcoredump file, writes metadata from `struct ath10k`, and appends selected TLVs for register dump, copy-engine data, and RAM dump. `ath10k_coredump_submit()` passes the final vmalloc buffer to `dev_coredumpv()`. `ath10k_coredump_create()`, `ath10k_coredump_register()`, `ath10k_coredump_unregister()`, and `ath10k_coredump_destroy()` manage persistent crash-data storage.

## Control Flow

Core object creation calls `ath10k_coredump_create()` to allocate `ar->coredump.fw_crash_data` unless coredumps are disabled by mask. After firmware/mac registration has discovered the target version, `ath10k_coredump_register()` allocates the optional RAM dump buffer if the RAM-data bit is enabled and a matching layout exists.

On crash, bus-specific handlers call `ath10k_coredump_new()` and then populate register, CE, and RAM fields. This file does not perform bus reads itself; PCI, SDIO, SNOC, and CE code fill `fw_crash_data`. During recovery, `ath10k_core_restart()` calls `ath10k_coredump_submit()`, which builds a single binary dump with fixed header metadata and requested TLVs.

## State and Persistence

Persistent in-memory state is one `struct ath10k_fw_crash_data` per device, allocated for the device lifetime. The RAM dump buffer may be large and is allocated at registration based on hardware layout. Per-crash mutable fields include GUID, timestamp, register snapshot, CE snapshot, and RAM buffer contents. The devcoredump subsystem owns the submitted buffer after `dev_coredumpv()`.

The user-visible persistence contract is the binary dump file ABI: `df_magic`, version, ath10k/device/firmware/kernel metadata, and TLV records. Endianness is normalized through little-endian fields.

## Dependencies and Integration Points

The file depends on `CONFIG_DEV_COREDUMP`, `linux/devcoredump.h`, `init_utsname()`, ath10k hardware constants, `core.h` crash structures, `debug.h` logging, and the global `ath10k_coredump_mask` defined in `core.c`. Bus crash handlers integrate by using the exported `ath10k_coredump_new()` and memory-layout helpers. `core.c` also uses `_ath10k_coredump_get_mem_layout()` for IRAM backup even when RAM dumps are disabled.

## Risks

The memory layout tables are user-space ABI-adjacent and hardware-sensitive. Incorrect ranges can hang the bus, miss critical crash data, or read invalid target memory. `ath10k_coredump_destroy()` assumes `fw_crash_data` is non-NULL; callers must preserve create/destroy ordering, especially when coredump mask disables allocation. `ath10k_coredump_unregister()` frees `ramdump_buf` without clearing the pointer, while destroy frees and clears if still present; normal lifecycle must not call unregister/destroy in an order that double-frees. Dump size calculations rely on region lengths and preallocated `ramdump_buf_len` matching bus fill logic.

## Test Signals

Important signals are correct layout selection for each bus/hardware tuple, no layout for unsupported hardware, successful RAM buffer allocation only when mask enables RAM data, valid devcoredump output with `ATH10K-FW-DUMP` magic, correctly sized TLVs matching mask bits, crash recovery submitting dumps after simulated firmware crashes, and no bus hangs while PCI/SDIO/SNOC dump readers honor section tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/coredump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/coredump.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/coredump.h

## Purpose

`coredump.h` defines the ath10k firmware crash dump ABI and the compile-time interface between core recovery, bus crash collectors, and devcoredump packaging. It describes dump TLVs, file header format, RAM-region descriptors, memory layout tables, and inline no-op stubs when `CONFIG_DEV_COREDUMP` is disabled.

## Important APIs and Types

`ATH10K_FW_CRASH_DUMP_VERSION` is the binary file version. `enum ath10k_fw_crash_dump_type` defines TLV payloads for register dumps, CE data, and RAM data. `struct ath10k_tlv_dump_data` is the generic TLV envelope. `struct ath10k_dump_file_data` is the top-level file header containing magic, length, version, GUID, chip/bus/target/firmware/radio metadata, kernel version, timestamp, reserved space, and variable TLV data.

`struct ath10k_dump_ram_data_hdr` prefixes each dumped memory region with region type, start, and payload length. `enum ath10k_mem_region_type` is marked as user-space ABI and covers REG, DRAM, AXI, IRAM1, IRAM2, IOSRAM, IOREG, and MSA. `ATH10K_MAGIC_NOT_COPIED` is the fill byte for holes in partially copied regions.

`struct ath10k_mem_section`, `struct ath10k_mem_region`, and `struct ath10k_hw_mem_layout` describe safe readable regions per hardware version and bus. Sections must be strictly ordered because bus dump processing depends on range order.

The real API under `CONFIG_DEV_COREDUMP` exposes submit, new crash data, create/register/unregister/destroy, and memory layout lookup functions. The disabled-config branch supplies stubs so callers do not need extensive ifdefs.

## Control Flow and State

The header establishes a two-phase lifecycle: allocate generic crash data during core object creation, then register/allocate layout-dependent RAM storage after hardware target information is available. Crash collectors call `ath10k_coredump_new()` under `dump_mutex` to stamp GUID/time and then fill the shared `struct ath10k_fw_crash_data` declared in `core.h`. Recovery later calls `ath10k_coredump_submit()`.

The layout lookup split is deliberate: `ath10k_coredump_get_mem_layout()` respects the global mask, while `_ath10k_coredump_get_mem_layout()` returns layouts independent of mask for non-dump features such as IRAM recovery.

## Dependencies and Integration Points

The header includes `core.h` and exports `ath10k_coredump_mask`, tying dump behavior to the module parameter in `core.c`. Bus implementations consume the memory-region types and section metadata to know what to read. User-space dump decoders depend on the struct layout, magic, version, TLV ids, region type enum values, little-endian fields, and the not-copied fill marker.

## Risks

Because several structs are dump-file ABI, changing field order, sizes, enum values, packing, or magic strings can break existing analyzers. Section ordering requirements are documented but not enforced by the type system. Inline stubs must stay semantically safe for callers that expect allocation or layout lookup to be optional. The stub `ath10k_coredump_new()` returns NULL, so bus crash code must continue to tolerate disabled devcoredump builds.

## Test Signals

Build coverage with `CONFIG_DEV_COREDUMP=y` and disabled is essential. Dump parser tests should validate magic, version, TLV sequence, little-endian metadata, and RAM region headers. Runtime tests should cover mask combinations for register-only, CE-only, RAM-enabled, and disabled dumps, plus hardware without a matching layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/coredump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/debug.c

## Purpose

`debug.c` implements ath10k logging helpers, firmware/board/boot information printing, debugfs control and inspection files, firmware statistics aggregation, TPC statistics retrieval, ethtool statistics, crash simulation controls, register/memory access hooks, and runtime debug feature toggles.

## Important APIs and Functions

Always-built logging helpers are `ath10k_info()`, `ath10k_err()`, and `ath10k_warn()`, all of which log through the device and tracepoints. `ath10k_debug_print_hwfw_info()`, `ath10k_debug_print_board_info()`, `ath10k_debug_print_boot_info()`, and exported `ath10k_print_driver_info()` summarize firmware, board, Kconfig, checksums, HTT/WMI versions, calibration mode, raw mode, and hardware crypto state.

Under `CONFIG_ATH10K_DEBUGFS`, key exported functions are `ath10k_debug_create()`, `ath10k_debug_register()`, `ath10k_debug_start()`, `ath10k_debug_stop()`, `ath10k_debug_unregister()`, `ath10k_debug_destroy()`, `ath10k_debug_fw_stats_process()`, `ath10k_debug_fw_stats_request()`, `ath10k_debug_tpc_stats_process()`, and `ath10k_debug_tpc_stats_final_process()`.

Debugfs files include `fw_stats`, `fw_reset_stats`, `wmi_services`, `simulate_fw_crash`, `reg_addr`, `reg_value`, `mem_value`, `chip_id`, `htt_stats_mask`, `htt_max_amsdu_ampdu`, `fw_dbglog`, `cal_data`, `nf_cal_period`, `ani_enable`, DFS controls/statistics, `pktlog_filter`, `quiet_period`, `tpc_stats`, `btcoex`, `peer_stats`, `enable_extd_tx_stats`, `fw_checksums`, `sta_tid_stats_mask`, `tpc_stats_final`, `warm_hw_reset`, `ps_state_enable`, and `reset_htt_stats`, with several gated by firmware service bits or Kconfig.

Under `CONFIG_ATH10K_DEBUG`, `__ath10k_dbg()` and `ath10k_dbg_dump()` implement debug-mask and tracepoint-backed verbose logging and hex dumps.

## Control Flow

Debug storage is allocated in `ath10k_debug_create()` before registration: calibration data buffer and firmware stats list heads. `ath10k_debug_register()` creates the per-phy `ath10k` debugfs directory after firmware capability discovery so service-gated files can be conditionally exposed. `ath10k_debug_start()` runs during firmware start and applies configured HTT stats polling, firmware dbglog mask, pktlog filter, and noise-floor calibration period. `ath10k_debug_stop()` snapshots calibration data when possible, cancels periodic HTT stats work without synchronous cancellation to avoid deadlock, and disables pktlog.

Firmware stats flow is request/response oriented. `ath10k_debug_fw_stats_request()` resets aggregate state, repeatedly sends WMI stats requests, waits on `fw_stats_complete`, and stops when `fw_stats_done` is observed. `ath10k_debug_fw_stats_process()` parses WMI stats skb payloads, handles multi-event ping-pong semantics, updates station RX duration for peer stats, splices pdev/vdev/peer lists, bounds peer/vdev growth, and completes waiters.

Several debugfs writes directly affect firmware. Crash simulation sends WMI force-hang, invalid vdev commands, assert-trigger install-key commands, or queues hardware restart. Register and memory files use HIF read/write or diagnostic windows. HTT controls send HTT stats/aggr commands. ANI, NF calibration period, pktlog, quiet period, BT coexistence, peer stats, warm reset, and PS state toggles send WMI pdev commands or trigger recovery.

## State and Persistence

Debugfs writes persist in `struct ath10k_debug` or adjacent `struct ath10k` fields for the life of the driver object: firmware dbglog mask/level, HTT stats mask/reset mask, register address, NF calibration period, calibration data snapshot, extended TX stats enable, TPC stats, DFS stats, pktlog filter, peer stats flag, BT coexistence flag, station TID stats mask, and PS-state enable. No on-disk persistence is performed.

Most debug operations are guarded by `conf_mutex` and state checks for `ATH10K_STATE_ON`, `ATH10K_STATE_UTF`, or `ATH10K_STATE_RESTARTED`. Shared stats lists and counters use `data_lock`.

## Dependencies and Integration Points

The file integrates with debugfs, tracepoints, firmware loader CRCs, WMI operations, HTT operations, HIF diagnostic reads/writes, mac80211 ethtool stats hooks, DFS detector, thermal throttling, core recovery, and core firmware metadata. It is tightly coupled to `core.h` state layout and to WMI service bits because debugfs file availability reflects firmware capability.

## Risks

Debugfs exposes powerful write paths: arbitrary register/memory writes, forced firmware crashes, warm resets, runtime firmware parameter changes, and recovery triggers. These must stay root-only or appropriately permissioned. Several paths allocate buffers based on user read/write sizes (`mem_value`) or fixed 1 MiB stats buffers; large reads can stress memory. Stats aggregation relies on firmware event ordering and could drop or misinterpret malformed stats. `ath10k_tpc_stats_final_open()` requests final TPC stats but fills from `ar->debug.tpc_stats`, which is a notable behavior to verify because a separate `tpc_stats_final` pointer exists.

## Test Signals

Test through debugfs file creation under different Kconfig and WMI service combinations, fw stats read success and timeout behavior, ethtool stats fallback to zero when no stats exist, crash simulation triggering recovery/coredump, register/memory access returning `-ENETDOWN` when firmware is down, pktlog/HTT polling start-stop cancellation without workqueue deadlocks, and lockdep coverage around stats processing and debugfs reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/debug.h

## Purpose

`debug.h` declares ath10k logging, debug masks, packet-log metadata, debugfs APIs, station debugfs hooks, stats helpers, and compile-time stubs for builds without debugfs or verbose debugging. It is the public debug interface consumed by core, bus, WMI, HTT, RX/TX, and mac80211 integration code.

## Important APIs and Types

`enum ath10k_debug_mask` defines bitmask categories for PCI, WMI, HTC, HTT, MAC, boot, dumps, management, data, BMI, regulatory, testmode, bus-specific logging, QMI, station logging, and `ATH10K_DBG_ANY`. The global `ath10k_debug_mask` is declared here and defined as a module parameter in `core.c`.

`enum ath10k_pktlog_filter` defines firmware packet log event filters for RX, TX, rate-control find/update, debug print, peer stats, and any. `enum ath10k_dbg_aggr_mode`, `enum ath_pktlog_type`, and packed `struct ath10k_pktlog_hdr` support debug aggregation and packet-log payload interpretation. `ATH10K_FW_STATS_BUF_SIZE`, `ATH10K_TX_POWER_MAX_VAL`, and `ATH10K_TX_POWER_MIN_VAL` define shared debug limits.

Always-available declarations include `ath10k_info()`, `ath10k_err()`, `ath10k_warn()`, hardware/firmware/board/boot print helpers, and `ath10k_print_driver_info()`. With `CONFIG_ATH10K_DEBUGFS`, the header declares debug lifecycle, firmware/TPC stats processing, dbglog handling, ethtool stats hooks, inline accessors for dbglog mask/level and extended TX stats, and the DFS stat increment macro. Without debugfs, equivalent stubs either return success/default values or free passed TPC allocations.

With `CONFIG_MAC80211_DEBUGFS`, station debugfs and RX TID stats update functions are declared; otherwise no-op stubs are used. With `CONFIG_ATH10K_DEBUG`, verbose debug and dump functions are declared; otherwise they compile away.

## Control Flow and Integration

The `ath10k_dbg()` macro avoids calling `__ath10k_dbg()` unless the mask is enabled or the tracepoint is active. This keeps hot paths cheap while preserving tracing support. Debugfs lifecycle functions are called from `core.c` during object creation, firmware start/stop, registration, unregistration, and destroy. Stats process functions are called from WMI event handlers; station TID stats hooks are called from RX/HTT paths.

## State and Persistence

The header owns no storage except declarations, but it exposes access to global `ath10k_debug_mask` and inline reads of `struct ath10k_debug` fields. Debug mask and coredump/debug parameters are runtime module state; debugfs settings persist only in memory until device removal.

## Dependencies and Integration Points

`debug.h` includes `trace.h` and Linux types and relies on `struct ath10k`, mac80211 types, skb, ethtool stats, and HTT RX indication types via surrounding includes. It is included widely because the lightweight logging macros are used throughout ath10k.

## Risks

Debug mask values are effectively user-facing through module parameters and trace expectations; changing them can break operational debugging. Stub behavior must match caller assumptions when debugfs or debug logging is disabled. The `ath10k_dbg()` macro references tracepoint availability, so trace header changes can affect compilation. Packed packet-log headers and filter bit values must stay aligned with firmware/userspace tooling.

## Test Signals

Build matrix coverage is the main signal: `CONFIG_ATH10K_DEBUGFS`, `CONFIG_MAC80211_DEBUGFS`, and `CONFIG_ATH10K_DEBUG` enabled and disabled. Runtime signals include debug-mask logging only when enabled, tracepoints still receiving debug messages when active, no-op stubs not changing behavior in production builds, and successful ethtool/debugfs integration when debugfs is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/debug.h -->
