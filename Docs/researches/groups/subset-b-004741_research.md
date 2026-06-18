# Research: subset-b-004741

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/ce.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/ce.c

## Purpose
Implements ath12k Copy Engine host-side transport rings. CE pipes are the low-level DMA path used by HTC/WMI/firmware messaging and some data paths to move sk_buffs between host and target firmware through HAL SRNG descriptors.

## Important APIs, Types, And Functions
Exports `ath12k_ce_alloc_pipes()`, `ath12k_ce_init_pipes()`, `ath12k_ce_free_pipes()`, `ath12k_ce_cleanup_pipes()`, `ath12k_ce_send()`, `ath12k_ce_per_engine_service()`, `ath12k_ce_rx_post_buf()`, `ath12k_ce_poll_send_completed()`, `ath12k_ce_get_shadow_config()`, and `ath12k_ce_get_attr_flags()`. The internal helpers allocate coherent descriptor rings, post RX buffers, reap destination status entries, reap source completions, and configure MSI/shadow-register parameters.

## Control Flow
Probe allocates pipe rings from `hw_params->host_ce_config`, then firmware-ready flow initializes SRNG rings and posts RX buffers. TX maps an skb before `ath12k_ce_send()`, which writes a HAL CE source descriptor and records the skb by ring index. Interrupt or polling service calls `ath12k_ce_per_engine_service()`, which reaps TX completions and invokes receive callbacks after unmapping and length-validating RX buffers. RX buffers are replenished immediately; allocation failures arm `rx_replenish_retry`.

## State And Persistence
State is in `ab->ce.ce_pipe[]`: source, destination, status rings, cached `write_index`/`sw_index`, skb owner arrays, `rx_buf_needed`, callbacks, and `ce_lock`. DMA-coherent descriptor memory persists for device lifetime. Posted RX skbs persist until firmware fills them or cleanup unmaps them. Shadow CE register config is cached in `ab->qmi.ce_cfg`.

## Dependencies And Integration Points
Depends on HAL SRNG/CE descriptor helpers, HIF MSI helpers, hw params, DMA APIs, timers, sk_buffs, and debug logging. It integrates with QMI startup via shadow config, HTC/WMI through CE pipes, and crash recovery through cleanup and crash-flush checks.

## Risks
Ring accounting must stay synchronized with HAL SRNG ownership; mismatched indices can leak skbs or corrupt DMA ownership. `ath12k_ce_cleanup_pipes()` only polls disabled-interrupt TX rings and has a note questioning full TX cleanup. RX replenish failures can degrade firmware messaging until retry succeeds. Lock ordering between `ce_lock` and SRNG locks is part of the correctness contract.

## Test Signals
Boot should show CE allocation/init success and WMI/HTC readiness. Stress WMI traffic, firmware restart, and low-memory RX replenish paths. Exercise interrupt-disabled pipes to verify polling completions. DMA debug, lockdep, and KASAN are useful for mapping lifetime and lock-order regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/ce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/ce.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/ce.h

## Purpose
Defines the Copy Engine interface and state shared by ath12k core, HAL, QMI startup, and transport users. It describes CE pipe direction, firmware-visible service mappings, per-platform pipe attributes, and host ring bookkeeping.

## Important APIs, Types, And Functions
Key constants include `CE_COUNT_MAX`, `CE_ATTR_BYTE_SWAP_DATA`, `CE_ATTR_DIS_INTR`, pipe direction values, platform CE interrupt-enable register addresses, `CE_RING_IDX_INCR()`, and `ATH12K_CE_RX_POST_RETRY_JIFFIES`. Key structures are `service_to_pipe`, `ce_pipe_config`, `ce_ie_addr`, `ce_remap`, `ce_attr`, `ath12k_ce_ring`, `ath12k_ce_pipe`, and `ath12k_ce`. The header declares all CE lifecycle, send, service, polling, and shadow-config functions.

## Control Flow
The header establishes the contract used by `ce.c`: platform `ce_attr` entries drive ring allocation and callbacks; QMI receives `service_to_pipe` and `ce_pipe_config`; core calls allocation, initialization, RX posting, service, cleanup, and free in probe/start/recovery/teardown order.

## State And Persistence
`ath12k_ce_ring` persists DMA-coherent descriptor base addresses, aligned CE/host addresses, ring size masks, HAL ring id, and an skb flexible array. `ath12k_ce_pipe` persists callbacks, ring pointers, RX buffer demand, pipe attributes, and timestamps. `ath12k_ce` stores up to 16 pipes plus the global CE spinlock and high-priority update timers.

## Dependencies And Integration Points
Includes Linux DMA/sk_buff concepts indirectly through declared structures and integrates with `ath12k_base`, QMI firmware configuration, HAL ring setup, and platform `hw_params`.

## Risks
`CE_RING_IDX_INCR()` assumes ring sizes are powers of two. Shared firmware structures must remain layout-compatible and little-endian. `CE_COUNT_MAX` must cover platform `ce_count`. Callback pointers in `ce_attr` are trusted by runtime receive processing.

## Test Signals
Compile coverage across all supported hardware configs verifies structure and constant use. Boot on IPQ/QCN/WCN variants validates CE count, register addresses, and firmware-visible config. Ring wraparound and interrupt-disabled TX polling are the important runtime signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/ce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/cmn_defs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/cmn_defs.h

## Purpose
Provides small shared capacity constants used across ath12k multi-radio and multi-link code. It centralizes limits derived from maximum devices, radios per device, mac80211 MLD links, and MU group IDs.

## Important APIs, Types, And Functions
Defines `MAX_RADIOS` as 2, `ATH12K_MAX_DEVICES` as 3, `ATH12K_GROUP_MAX_RADIO` as devices times radios, `ATH12K_SCAN_MAX_LINKS`, `ATH12K_NUM_MAX_LINKS`, and `MAX_MU_GROUP_ID`. It includes mac80211 for `IEEE80211_MLD_MAX_NUM_LINKS`.

## Control Flow
No executable flow. These constants size arrays and bitmaps used by core, scan, MLO, vif, station, and statistics paths.

## State And Persistence
No state is stored here, but the constants determine persistent structure sizes such as per-group hardware link arrays and link pointer arrays in `core.h`.

## Dependencies And Integration Points
The file couples ath12k internal limits to mac80211 MLD link capacity. It is consumed by `core.h` and other shared ath12k headers.

## Risks
Changing these values changes ABI-like in-kernel structure sizes and may expose hidden assumptions in firmware, hardware grouping, scan link allocation, and debug stats arrays. `MAX_RADIOS` must remain consistent with `ath12k_base.pdevs[MAX_RADIOS]`.

## Test Signals
Build coverage catches most array-size fallout. Runtime validation requires multi-radio and multi-device MLO configurations, plus scan/link creation paths that use the maximum link counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/cmn_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/core.c

## Purpose
Owns ath12k device lifecycle: module parameters, firmware and board-data loading, QMI firmware-ready handling, CE/DP/WMI/HTC startup, mac80211 group registration, MLO setup, suspend/resume, crash recovery, reset coordination, SMBIOS/DT grouping, panic notification, and final allocation/free.

## Important APIs, Types, And Functions
Exports `ath12k_debug_mask`, `ath12k_ftm_mode`, suspend/resume functions, firmware/board/regdb fetch helpers, peer/station capacity helpers, reserved memory lookup, `ath12k_core_qmi_firmware_ready()`, recovery helpers, group cleanup/unassign, MLO capability setup, firmware stats init/free/reset, memory mode selection, `ath12k_core_pre_init()`, `ath12k_core_init()`, `ath12k_core_deinit()`, `ath12k_core_alloc()`, and `ath12k_core_free()`. Internal work functions handle RFKill, 11d updates, restart, and reset.

## Control Flow
Probe allocates `ath12k_base`, registers panic handling, assigns the device to a hardware group, and once every group member is probed powers up SOCs through QMI/HIF. Firmware-ready starts firmware, initializes CE pipes and common DP, starts WMI/HTC/HIF, waits for service/unified-ready events, initializes REO and HTT, marks the base started, and starts the whole group when all devices are ready. Group start allocates/registers mac80211 hardware, sets up MLO if supported, creates pdev resources, enables IRQs, and configures rfkill. Teardown reverses those layers. Reset collects coredump data, flushes queues/completions, powers devices down, waits for group partners, resets MLO memory, and powers group members back up for restart.

## State And Persistence
Uses global `ath12k_hw_group_list` under `ath12k_hw_group_mutex`. Per-device state lives in `ath12k_base`: flags, completions, workqueues, QMI/WMI/HTC/DP/CE/HAL objects, pdev arrays, regulatory data, firmware files, debug/coredump state, ACPI/SMBIOS data, and group links. Group state tracks number of devices probed/started, registered flags, MLO memory, WSI DT nodes, and mac80211 hardware objects.

## Dependencies And Integration Points
Integrates with Linux module params, firmware loader, remoteproc/devicetree/SMBIOS/ACPI, panic notifiers, HIF bus ops, QMI, HAL, CE, DP, HTC, WMI, mac80211, regulatory, thermal, debugfs, WOW, peer tables, and coredump.

## Risks
Startup and recovery are heavily ordered; missing cleanup on partial failure can leave firmware, IRQs, DP rings, or group refs inconsistent. Grouping by DT WSI nodes and MLO readiness depends on all devices following the same state transitions. Reset throttling protects against infinite recovery but can leave hardware wedged. Board-data matching parses firmware TLVs and must reject malformed lengths. Suspend/resume only proceeds for supported devices with hardware off, so state predicates must remain accurate.

## Test Signals
Probe on single-device and multi-device MLO hardware, firmware API1/API2 board fallback, regdb fallback, rfkill-capable targets, suspend/resume, simulated firmware assert, repeated crash recovery, and module unload are key signals. Lockdep should cover group/core mutex ordering; firmware logs and mac80211 registration indicate successful lifecycle sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/core.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/core.h

## Purpose
Defines the central ath12k object model and public core interface. Nearly every subsystem consumes this header for per-device, per-radio, per-vif, per-station, firmware stats, MLO, regulatory, recovery, debug, and datapath state.

## Important APIs, Types, And Functions
Important enums cover BDF search mode, WME AC, crypto mode, skb flags, hardware revisions, firmware modes, SMBIOS country-code mode, scan and 11d states, group and device flags, RX error buckets, stats categories, hardware state, and device family. Major structures include `ath12k_skb_cb`, `ath12k_skb_rxcb`, `ath12k_link_vif`, `ath12k_vif`, `ath12k_link_sta`, `ath12k_sta`, `ath12k`, `ath12k_hw`, `ath12k_pdev_cap`, `ath12k_pdev`, `ath12k_hw_group`, `ath12k_base`, and firmware stats records. Inline helpers convert between mac80211 private objects and ath12k objects, map bus names, build firmware paths, access DP/core pointers, and stringify scan state.

## Control Flow
The header does not implement full flows, but it defines the state machines used by `core.c`, `mac.c`, DP, WMI, and debugfs: scan transitions, hardware restart states, device flags for crash/recovery/registration, MLO group membership, and completion objects for WMI commands.

## State And Persistence
Persistent driver state is rooted at `ath12k_base`; per-radio runtime state is in `ath12k`; registered mac80211 aggregate state is in `ath12k_hw`; multi-device grouping is in `ath12k_hw_group`. It also stores long-lived firmware handles, regulatory domains, pdev capability tables, ACPI data, coredump buffers, workqueues, completions, IDRs, RCU pdev pointers, and rhashtables.

## Dependencies And Integration Points
Includes Linux IRQ, DMI, firmware, OF, panic notifier, average, rhashtable, and many ath12k subsystem headers. It is the integration boundary between bus drivers, mac80211, WMI/QMI/HTC/HAL/DP, debugfs, coredump, thermal, regulatory, and WOW.

## Risks
Because this is the shared state contract, field lifetime and locking comments are critical. Several members are protected by `data_lock`, `base_lock`, `core_lock`, `hw_mutex`, group mutex, RCU, or wiphy mutex; incorrect access can race with recovery or interface teardown. Flexible-array and private-data casts must remain compatible with mac80211 storage sizes.

## Test Signals
Builds with debugfs/coredump/ACPI combinations, sparse/lockdep, and all bus variants are important. Runtime signals include station/vif MLO creation, recovery state transitions, scan timeout/completion behavior, debug stats reads, and firmware path selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/coredump.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/coredump.c

## Purpose
Provides the enabled coredump implementation for firmware crash capture. It maps QMI memory-region types to ath12k dump TLV types, asks the bus/HIF layer to download dump memory, and uploads the assembled dump through Linux devcoredump.

## Important APIs, Types, And Functions
`ath12k_coredump_get_dump_type()` translates `ath12k_qmi_target_mem` values into `ath12k_fw_crash_dump_type`. `ath12k_coredump_collect()` delegates to `ath12k_hif_coredump_download()`. `ath12k_coredump_upload()` is a workqueue handler that calls `dev_coredumpv()` with `ab->dump_data` and `ab->ath12k_coredump_len`.

## Control Flow
Recovery calls collect before pre-reconfiguration. HIF/bus code fills `ab->dump_data` and schedules `ab->dump_work`. The upload worker logs the upload, hands buffer ownership to devcoredump, and clears the pointer.

## State And Persistence
Uses `ath12k_base.dump_data` and `ath12k_base.ath12k_coredump_len`. After `dev_coredumpv()`, ownership leaves the driver. Dump type mapping treats BDF/CALDB regions as no-dump and unknown regions as max/invalid.

## Dependencies And Integration Points
Depends on Linux `devcoredump`, HIF coredump download support, QMI memory-region enums, and debug logging. Integrated from `core.c` reset work and initialized as `ab->dump_work` in allocation.

## Risks
Ownership transfer is strict: `dev_coredumpv()` owns the buffer after upload. Incorrect length or partially filled dump data would expose malformed devcoredumps. Unsupported region mappings can silently omit data needed for diagnosis.

## Test Signals
Simulate firmware assert and verify `/sys/class/devcoredump` receives an ath12k dump. Validate region TLVs on hardware with HOST DDR, M3, pageable, and MLO global memory. Ensure repeated crashes do not reuse freed `dump_data`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/coredump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/coredump.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/coredump.h

## Purpose
Defines the ath12k firmware coredump file format, TLV payload format, dump type enum, and no-op fallbacks when coredump support is disabled.

## Important APIs, Types, And Functions
Defines `ATH12K_FW_CRASH_DUMP_V2`, `COREDUMP_TLV_HDR_SIZE`, `enum ath12k_fw_crash_dump_type`, `struct ath12k_tlv_dump_data`, and `struct ath12k_dump_file_data`. The enabled declarations are `ath12k_coredump_get_dump_type()`, `ath12k_coredump_upload()`, and `ath12k_coredump_collect()`; disabled builds return `FW_CRASH_DUMP_TYPE_MAX` and no-op.

## Control Flow
No runtime flow beyond compile-time selection by `CONFIG_ATH12K_COREDUMP`. The structures are filled by HIF/core coredump code and consumed by Linux devcoredump readers.

## State And Persistence
The dump file header persists magic, total length, version, chip/QRTR/bus IDs, GUID, timestamps, reserved bytes, and trailing TLV data. TLV records persist a little-endian type and length followed by aligned data.

## Dependencies And Integration Points
Depends on QMI memory type declarations and Linux GUID/little-endian types through included users. It is included by `core.h`, making coredump state part of `ath12k_base`.

## Risks
This is a binary format contract; changing packed layout breaks tooling. Comments still mention ath11k in one TLV field comment, which is harmless but confusing. Disabled-build stubs must preserve call-site behavior during recovery.

## Test Signals
Build with and without `CONFIG_ATH12K_COREDUMP`. Validate generated dump headers with external parsers and confirm TLV lengths align to the collected memory regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/coredump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dbring.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dbring.c

## Purpose
Implements direct-buffer rings used for firmware modules that DMA data into host-provided buffers, currently structured around spectral/direct-buffer release events. It manages SRNG refill descriptors, DMA mapping, buffer ID cookies, WMI configuration, event handling, and cleanup.

## Important APIs, Types, And Functions
Exports `ath12k_dbring_set_cfg()`, `ath12k_dbring_wmi_cfg_setup()`, `ath12k_dbring_buf_setup()`, `ath12k_dbring_srng_setup()`, `ath12k_dbring_get_cap()`, `ath12k_dbring_buffer_release_event()`, `ath12k_dbring_srng_cleanup()`, and `ath12k_dbring_buf_cleanup()`. Internal helpers replenish one buffer and fill as many buffers as possible.

## Control Flow
Setup creates a DP SRNG, derives max buffers and HP/TP addresses, fills the ring with aligned DMA buffers, and sends WMI DMA ring config. Replenish maps the aligned payload, allocates an IDR id, encodes pdev/buffer ID into a cookie, and writes a HAL RX buffer address descriptor. On firmware release events, the code validates pdev and entry counts, looks up the active pdev under RCU, selects the module ring, removes buffers from the IDR, unmaps DMA, invokes the module handler, zeroes the buffer, and attempts atomic replenishment.

## State And Persistence
`ath12k_dbring` stores the refill SRNG, IDR of live buffers, buffer limits, pdev id, alignment/size, WMI event pacing, handler pointer, and HP/TP DMA addresses. Each buffer persists its DMA address and flexible payload allocation until event release or cleanup.

## Dependencies And Integration Points
Depends on DP SRNG setup/cleanup, HAL SRNG and RX buffer address helpers, WMI direct-buffer config/events, Linux IDR, DMA mapping, RCU pdev activity, and module-specific handlers such as spectral.

## Risks
The switch in `ath12k_dbring_buffer_release_event()` currently does not assign a ring for `WMI_DIRECT_BUF_SPECTRAL` in this file, so correctness depends on future or external wiring; as shown, unsupported/no ring returns `-EINVAL`. Replenish errors during event processing are ignored after handler invocation. IDR and SRNG locks must protect buffer ownership consistently to avoid double unmap or leaks.

## Test Signals
Spectral/direct-buffer enablement should configure WMI ring args and receive release events. DMA debug can catch mapping lifetime bugs. Force ring full, IDR exhaustion, inactive pdev, mismatched metadata counts, and cleanup during active buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dbring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dbring.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dbring.h

## Purpose
Declares the direct-buffer ring data model and public API used by modules that receive firmware DMA payloads through host refill rings.

## Important APIs, Types, And Functions
Defines `ath12k_dbring_element` for one DMA buffer, `ath12k_dbring_data` passed to handlers, `ath12k_dbring_buf_release_event` wrapping WMI release entries and metadata, `ath12k_dbring_cap` from firmware capability discovery, and `ath12k_dbring` as the persistent ring object. Declares setup, configuration, capability lookup, event handling, and cleanup functions.

## Control Flow
No implementation flow, but the API order is SRNG setup, buffer setup from capabilities, handler/event pacing config, WMI config, release-event processing, then SRNG/buffer cleanup.

## State And Persistence
The ring owns a DP refill SRNG, IDR of live buffers, IDR spinlock, firmware-visible tail/head pointer addresses, max buffer count, pdev id, buffer sizing/alignment, response pacing, timeout, and a handler callback.

## Dependencies And Integration Points
Includes Linux types, IDR, spinlock, and `dp.h`. It references WMI direct-buffer modules and WMI DMA release metadata structures, making it a bridge between DP/HAL rings and WMI event parsing.

## Risks
Callers must initialize the IDR and lock before buffer setup; the header does not encode that lifecycle. Handler callbacks execute from event processing context and must respect locking and allocation constraints. Capability fields must match firmware-provided minimum alignment and size.

## Test Signals
Compile users for all direct-buffer modules. Runtime should verify capability lookup, WMI config arguments, handler data alignment, and cleanup with outstanding buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/dbring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debug.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debug.c

## Purpose
Provides ath12k logging helpers and optional debug dump support. It standardizes info/error/warn/debug output against the device associated with `ath12k_base`.

## Important APIs, Types, And Functions
Exports `ath12k_info()`, `ath12k_err()`, `__ath12k_warn()`, `__ath12k_dbg()` when debug is enabled, and `ath12k_dbg_dump()` when debug is enabled. The implementation uses `va_format`, `dev_info`, `dev_err`, `dev_warn_ratelimited`, `dev_printk`, `printk`, `dev_dbg`, and `hex_dump_to_buffer`.

## Control Flow
Regular info/error/warn functions format varargs and emit immediately. `ath12k_dbg()` macro in the header gates calls by `ath12k_debug_mask`; enabled debug prints route to `__ath12k_dbg()`. `ath12k_dbg_dump()` emits an optional message and then formats 16-byte hex lines when the selected mask is active.

## State And Persistence
This file holds no state except using global `ath12k_debug_mask` declared in `core.c`. Warn output is rate-limited by the kernel device logging path.

## Dependencies And Integration Points
Depends on `core.h`, `debug.h`, Linux vmalloc include, and kernel logging APIs. Used broadly by CE, core, dbring, debugfs, coredump, and other ath12k subsystems.

## Risks
Debug dump pointer arithmetic uses `const void *` arithmetic as accepted by kernel/GNU C. Excessive debug masks can produce high log volume, especially hex dumps. Warn rate limiting can hide repeated failures during tight loops.

## Test Signals
Build with and without `CONFIG_ATH12K_DEBUG`. Runtime module parameter `debug_mask` should gate debug lines and dumps; normal info/error/warn should work regardless of debug config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debug.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debug.h

## Purpose
Declares ath12k debug masks, logging APIs, global module parameters, and compile-time debug stubs/macros.

## Important APIs, Types, And Functions
Defines `enum ath12k_debug_mask` with masks for AHB, WMI, HTC, DP/HTT, MAC, boot, QMI, data, management, regulatory, testmode, HAL, PCI, DP TX/RX, WOW, CE, and any. Declares `ath12k_info()`, `ath12k_err()`, `__ath12k_warn()`, optional `__ath12k_dbg()`, and optional `ath12k_dbg_dump()`. Provides `ath12k_warn()`, `ath12k_hw_warn()`, `ath12k_dbg()`, and `ath12k_generic_dbg()` macros.

## Control Flow
`ath12k_dbg()` evaluates the mask once and only calls the debug function when the global mask enables it. Without `CONFIG_ATH12K_DEBUG`, debug functions compile to no-ops while info/error/warn remain available.

## State And Persistence
Declares external `ath12k_debug_mask` and `ath12k_ftm_mode`, both defined as module parameters in `core.c`.

## Dependencies And Integration Points
Includes `trace.h`, though trace emission is currently only marked as TODO in `debug.c`. Used across the driver as the common logging contract.

## Risks
`ath12k_warn(ab, ...)` assumes `ab` is non-null and has a valid device. Debug-only behavior can hide code path format warnings if not built with debug enabled, though printf annotations help.

## Test Signals
Compile both debug and non-debug configs. Validate each debug mask via module parameter and ensure generic debug with a null base prints with the fallback prefix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debugfs.c

## Purpose
Implements ath12k debugfs controls and diagnostics for SOC, pdev/radio, vif link, firmware stats, TPC power tables, extended RX stats, DP device stats, radar simulation, and firmware crash simulation.

## Important APIs, Types, And Functions
Exports `ath12k_debugfs_soc_create()`, `ath12k_debugfs_soc_destroy()`, `ath12k_debugfs_pdev_create()`, `ath12k_debugfs_register()`, `ath12k_debugfs_unregister()`, and `ath12k_debugfs_op_vif_add()`. Internal file operations cover `simulate_fw_crash`, `dfs_simulate_radar`, `tpc_stats`, `tpc_stats_type`, `ext_rx_stats`, `link_stats`, `device_dp_stats`, and firmware stats files for vdev/beacon/pdev. TPC helpers map preambles, modes, rate codes, and firmware arrays into printable per-chain power limits.

## Control Flow
SOC creation creates `/sys/kernel/debug/ath12k/<bus-dev>`. Pdev creation adds SOC-level crash simulation and DP stats. Radio registration creates `macN`, symlinks from mac80211 debugfs, optional radar simulation, TPC files, HTT stats, firmware stats, and extended RX stats. Read-open operations usually allocate a buffer, lock wiphy when needed, request firmware stats or TPC data over WMI, wait for completions, render text, and free data on release. Writes validate user input and send WMI commands or HTT filter updates.

## State And Persistence
Uses `ar->debug` for dentries, TPC type/request/completion/stats, RX filter, and extended RX stats enabled state. Firmware stats lists in `ar->fw_stats` are initialized for debugfs and reset after dumping. Link stats are copied under per-link spinlock. Debugfs dentries persist until unregister/destroy.

## Dependencies And Integration Points
Depends on mac80211 debugfs/wiphy locking, WMI commands/events, DP TX HTT RX filter setup, HTT debug stats registration, firmware stats dumping, core hardware state, pdev/radio capabilities, RCU pdev lookups, and Linux debugfs/file APIs.

## Risks
Debugfs operations can trigger firmware actions, including crash simulation, radar simulation, stats requests, and RX filter changes; permissions mitigate but do not remove operational risk. TPC formatting uses a fixed large buffer and complex firmware-provided arrays, so bounds and received TLV flags matter. Several reads require hardware state `ON`; races with recovery must be covered by wiphy/core state locking. Extended RX stats changes monitor filters and can affect datapath volume/performance.

## Test Signals
Mount debugfs and verify SOC/radio symlinks, firmware stats reads while interfaces are up/down, TPC timeout behavior, ext_rx_stats toggling, DP stats content, radar simulation on 5 GHz-capable radios, and firmware assert recovery through `simulate_fw_crash`. KASAN/lockdep help validate open/release and recovery races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debugfs.h

## Purpose
Declares the debugfs integration points and TPC formatting constants/enums. It also provides no-op stubs when debugfs is disabled.

## Important APIs, Types, And Functions
Enabled declarations include SOC create/destroy, radio register/unregister, vif debugfs add, pdev debugfs create, and inline accessors for extended RX stats state/filter. Constants define CCK/OFDM/HT/VHT/HE/EHT rate counts, NSS values, TPC wait time, invalid/max TPC values, table dimensions, modulation limit, and buffer size. Enums define WMI TPC preamble/bandwidth values, control-mode indices, and supported mode bits.

## Control Flow
No direct runtime flow. Compile-time `CONFIG_ATH12K_DEBUGFS` selects real functions and state accessors or no-op/false/zero stubs, allowing callers to avoid preprocessor branches.

## State And Persistence
The header does not store state; it exposes access to `ar->debug.extd_rx_stats` and `ar->debug.rx_filter` when debugfs exists. TPC constants determine allocation and formatting sizes in `debugfs.c`.

## Dependencies And Integration Points
References `ath12k_base`, `ath12k`, and mac80211 `ieee80211_hw`/`ieee80211_vif` types through declarations. Integrated with core startup, mac80211 vif creation, DP monitor filtering, and WMI TPC stats.

## Risks
`TPC_STATS_WAIT_TIME` is defined twice with the same value, which is benign but noisy. Rate and mode enum values must match firmware TPC data layout; mismatches lead to misleading debug output. Disabled stubs return false/zero, so production code must not depend on debugfs side effects.

## Test Signals
Build with `CONFIG_ATH12K_DEBUGFS=y` and disabled. Runtime TPC stats should fit the declared buffer and reflect expected preamble/mode mappings for 2/5/6 GHz and EHT puncturing cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/debugfs.h -->
