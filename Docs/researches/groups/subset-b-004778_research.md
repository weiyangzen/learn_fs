# Research: subset-b-004778

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/debugfs.c

## Purpose
`debugfs.c` builds the wil6210 debugfs control and inspection surface. It exposes ring/status-ring state, mailbox contents, raw firmware memory blobs, interrupt registers, station/reorder state, firmware version/capabilities, suspend counters, PMC capture controls, LED controls, link statistics, and several privileged write-only command paths. It is diagnostic glue around `wil6210_priv`, WMI helpers, TX/RX rings, PMC, power management, and firmware memory mappings.

## Important APIs, Types, And Functions
The local `enum dbg_off_type` and `struct dbg_off` describe debugfs entries backed by driver fields, static globals, or MMIO offsets. `wil6210_debugfs_init()` creates the top-level directory, allocates per-register `wil_debugfs_iomem_data`, initializes PMC state, and registers all files, blobs, ISR register directories, pseudo-ISR registers, and interrupt moderation counters. `wil6210_debugfs_remove()` recursively removes debugfs, frees helper state and latency histograms, and frees PMC memory without sending firmware commands during teardown.

Read-side show functions include `ring_show()`, `srings_show()`, `mbox_show()`, `txdesc_show()`, `status_msg_show()`, `rx_buff_mgmt_show()`, `bf_show()`, `temp_show()`, `link_show()`, `info_show()`, `sta_show()`, `mids_show()`, `wil_tx_latency_debugfs_show()`, `wil_link_stats_debugfs_show()`, `fw_capabilities_show()`, and `fw_version_show()`. Write-side controls include `wil_write_file_rxon()`, `wil_write_file_rbufcap()`, `wil_write_back()`, `wil_write_pmccfg()`, `wil_write_file_txmgmt()`, `wil_write_file_wmi()`, `wil_write_file_recovery()`, `wil_tx_latency_write()`, `wil_link_stats_write()`, `wil_link_stats_global_write()`, `wil_write_file_led_cfg()`, `wil_write_led_blink_time()`, `wil_write_suspend_stats()`, and `wil_compressed_rx_status_write()`.

## Control Flow
Initialization is table driven. `dbg_files[]` maps names to `file_operations`, while `dbg_wil_off[]`, `dbg_wil_regs[]`, `dbg_statics[]`, `isr_off[]`, `pseudo_isr_off[]`, and ITR tables map fields/registers to debugfs scalar files. Ring and mailbox readers acquire runtime PM and, where needed, `wil_mem_access_lock()` plus HALP votes before touching device memory. Writable entries parse user input, validate ranges, and issue WMI commands or update driver fields. Several show paths call firmware synchronously through WMI, for example beamforming, temperature, and link statistics.

## State And Persistence
Most state is live kernel/device state, not persistent storage. The file has static debug selector variables (`mem_addr`, descriptor/ring/status indices) shared across devices by design, noted in the source as a hack. Persistent-in-driver state includes `wil->dbg_data`, PMC context, latency histogram allocation per station, `wil->fw_version`, `wil->fw_capabilities`, suspend counters, and EDMA configuration flags. Debugfs removal must free allocations that can outlive open debug sessions.

## Dependencies And Integration Points
The file depends on Linux debugfs/seq_file, runtime PM, cfg80211, WMI command helpers, TX/RX descriptor formats, firmware mappings, power supply status, LED globals, and PMC APIs from `pmc.c`. It integrates with reset/suspend protection through runtime PM and `wil_mem_access_lock()`, with P2P/cfg80211 through management frame injection, and with WMI for control commands.

## Risks
The surface is powerful and should remain debugfs-only: raw WMI send, raw management transmit, register writes, RX-on control, aggregation control, and firmware recovery control can destabilize hardware. `wil_compressed_rx_status_write()` only blocks changes once interfaces are active; future EDMA config toggles need the same guard. Static debug selector variables are not per-device. Several show paths dereference live ring/state under limited locking, so teardown/NAPI synchronization assumptions matter.

## Test Signals
Useful signals include debugfs creation/removal under probe/remove, reading every show file while up/down/suspended, WMI failures from temperature/link stats/beamforming, PMC alloc/free/read error paths, invalid parser inputs for writable files, EDMA versus legacy ring displays, and lockdep/KASAN testing around teardown while debugfs files are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/ethtool.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/ethtool.c

## Purpose
`ethtool.c` provides the wil6210 ethtool hooks, currently focused on interrupt coalescing. It lets users inspect and configure RX/TX interrupt moderation thresholds while reusing cfg80211's standard driver-info implementation.

## Important APIs, Types, And Functions
`wil_ethtoolops_get_coalesce()` reads TX and RX interrupt timer control/threshold registers and reports `tx_coalesce_usecs` and `rx_coalesce_usecs`. `wil_ethtoolops_set_coalesce()` validates requested usec thresholds, rejects monitor mode, stores values in `wil->tx_max_burst_duration` and `wil->rx_max_burst_duration`, resumes the device through runtime PM, and invokes `wil->txrx_ops.configure_interrupt_moderation()`. `wil_set_ethtoolops()` installs the static `wil_ethtool_ops` table on a netdev.

## Control Flow
Both get and set operations serialize on `wil->mutex`. Get resumes the PCI device, reads legacy interrupt moderation registers (`RGF_DMA_ITR_TX_CNT_CTL`, `RGF_DMA_ITR_TX_CNT_TRSH`, `RGF_DMA_ITR_RX_CNT_CTL`, `RGF_DMA_ITR_RX_CNT_TRSH`), then autosuspends. Set rejects unsupported monitor-mode coalescing because monitor mode prefers timestamp precision, bounds values by `WIL6210_ITR_TRSH_MAX`, updates cached driver configuration, and asks the active TX/RX backend to reprogram moderation.

## State And Persistence
The configured values are stored in `wil6210_priv` and survive until driver reset/reconfiguration or module unload. The actual hardware state is rewritten through the TX/RX ops path when set, and also during firmware bring-up from `main.c`.

## Dependencies And Integration Points
This file depends on netdev ethtool APIs, cfg80211 driver info, runtime PM wrappers from `pm.c`, register helpers from `wil6210.h`, and interrupt moderation implementations in `interrupt.c`. `netdev.c` calls `wil_set_ethtoolops()` for every allocated VIF netdev.

## Risks
Only usec coalescing fields are honored; other ethtool coalescing fields are ignored and invalid values return `-EINVAL`. Register reads are legacy register specific, while set delegates through `txrx_ops`; EDMA behavior should be verified to ensure reported values remain meaningful. Runtime PM failures propagate directly.

## Test Signals
Exercise `ethtool -c` and `ethtool -C` while the device is active, suspended, in monitor mode, and using EDMA/legacy DMA. Check threshold boundary values above `WIL6210_ITR_TRSH_MAX`, runtime PM failure injection, and whether interrupts are reprogrammed after reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/fw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/fw.c

## Purpose
`fw.c` is the firmware container wrapper. It declares firmware and board files for module metadata, provides the 32-bit MMIO memset primitive required by wil6210 hardware, and includes `fw_inc.c`, which contains the parser and loader implementation.

## Important APIs, Types, And Functions
`MODULE_FIRMWARE()` advertises default Sparrow, Sparrow Plus, Talyn, and board-file names to userspace firmware tooling. `wil_memset_toio_32()` writes a repeated 32-bit value to MMIO using `__raw_writel()`, matching the driver's broader rule that device memory access must avoid 64-bit transactions on 64-bit hosts. Including `fw_inc.c` makes the static parser helpers share this translation unit and access `wil_memset_toio_32()`.

## Control Flow
The file has no standalone runtime entry point beyond helper inclusion. Firmware load is initiated elsewhere, primarily `wil_reset()` in `main.c`, which calls `wil_request_firmware()` and `wil_request_board()` implemented by the included `fw_inc.c`.

## State And Persistence
No persistent driver state is owned here. Firmware file names become module metadata. The memset helper mutates target device memory during firmware fill-record handling.

## Dependencies And Integration Points
It depends on Linux firmware APIs, module metadata, CRC support needed by `fw_inc.c`, and local firmware structures from `fw.h`. The wrapper integrates the parser into a translation unit with access to driver MMIO helpers and `wil6210_priv`.

## Risks
The loop in `wil_memset_toio_32()` assumes callers pass aligned sizes validated by `fw_inc.c`. Any new fill-record path must preserve the validation that sizes are at least one dword and dword aligned. Because `fw_inc.c` is included rather than compiled separately, symbol visibility and include order matter.

## Test Signals
Firmware images with fill records should be tested on 64-bit hosts. Build tests should catch include-order regressions. Firmware metadata can be checked with module tools to confirm expected firmware names are exposed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/fw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/fw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/fw.h

## Purpose
`fw.h` defines the on-disk/in-firmware record format consumed by the wil6210 firmware and board-file loader. It is the schema shared by parser code and reset-time firmware loading.

## Important APIs, Types, And Functions
The file defines `WIL_FW_SIGNATURE`, `WIL_FW_FMT_VERSION`, and `enum wil_fw_record_type`. Packed record types include `wil_fw_record_head`, `wil_fw_record_data`, `wil_fw_record_fill`, `wil_fw_record_comment`, `wil_fw_record_capabilities`, `wil_fw_record_concurrency`, `wil_fw_record_brd_file`, `wil_fw_record_action`, `wil_fw_record_direct_write`, `wil_fw_record_verify`, `wil_fw_record_file_header`, `wil_fw_record_gateway_data`, and `wil_fw_record_gateway_data4`. Magic constants identify capabilities, concurrency, and board metadata stored inside comment records.

## Control Flow
There is no executable control flow in the header. The parser in `fw_inc.c` reads a `wil_fw_record_head`, uses `type` and `size` to dispatch to a handler, and interprets the following packed structure according to the definitions here. The file header record must appear first, carries CRC and total data length, and may carry a version string using `WIL_FW_VERSION_PREFIX`.

## State And Persistence
The structures describe persistent firmware/board-file bytes. Runtime state derived from them includes firmware capability bitmaps, interface concurrency combinations, board-file target addresses and limits, firmware version text, and device memory contents written during firmware load.

## Dependencies And Integration Points
Types use Linux endian annotations and flexible array declarations. The records integrate with WMI capability enums, cfg80211 interface combinations, `wil6210_priv` firmware mapping, and board-file download logic.

## Risks
Every structure is `__packed` and endian-sensitive. Extending the format requires careful versioning because `fw_inc.c` rejects file-header versions greater than `WIL_FW_FMT_VERSION` and unknown record types. Variable-length records must be bounds-checked before dereference; this is especially important for concurrency and board metadata.

## Test Signals
Useful tests include malformed record sizes, unaligned lengths, unsupported header versions, bad signatures, bad CRCs, truncated variable arrays, unknown record types, and valid images containing each supported record type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/fw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/fw_inc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/fw_inc.c

## Purpose
`fw_inc.c` implements firmware and board-file verification, parsing, and download. It validates firmware containers, extracts capabilities and board metadata during a parse-only pass, writes data/fill/direct/gateway records to device memory during a load pass, and loads board files either at firmware-provided addresses or through the older firmware-file path.

## Important APIs, Types, And Functions
`wil_fw_verify()` checks dword alignment, header presence, file length, signature, format version, and CRC. `wil_fw_process()` iterates records and dispatches through `wil_fw_handlers[]`. Comment handlers parse capabilities (`fw_handle_capabilities()`), board-file entries (`fw_handle_brd_file()`), and cfg80211 concurrency limits (`fw_handle_concurrency()`). Load handlers include `fw_handle_data()`, `fw_handle_fill()`, `fw_handle_direct_write()`, `fw_handle_gateway_data()`, and `fw_handle_gateway_data4()`. Public entry points are `wil_request_firmware()`, `wil_request_board()`, and `wil_fw_verify_file_exists()`.

## Control Flow
`wil_request_firmware()` requests a firmware blob, clears previous board metadata, then loops over concatenated firmware sections. Each section is verified and processed either in parse mode or load mode. Parse mode only handles metadata records and file headers; load mode performs MMIO writes. Board loading first verifies the board file, then `wil_brd_process()` skips the header and writes each data record to the corresponding address/limit gathered from firmware metadata.

## State And Persistence
The parser mutates `wil->fw_capabilities`, `wil->fw_version`, `wil->brd_info`, `wil->num_of_brd_entries`, and device memory. It releases and reallocates board metadata per firmware request. Firmware bytes are not retained after `release_firmware()`.

## Dependencies And Integration Points
It depends on the Linux firmware loader, CRC32, WMI address translation (`wmi_buffer_block()`), 32-bit MMIO copy/fill helpers from `main.c` and `fw.c`, cfg80211 combination construction, and hardware firmware mappings. `main.c` uses it in reset/up paths; `pcie_bus.c` uses parse-only firmware requests to discover capabilities before the full load.

## Risks
This is a trust boundary for firmware files. Incorrect bounds checks can turn malformed firmware into MMIO corruption. Gateway writes poll with a fixed timeout and fail the load on busy hardware. Board-file processing assumes records match firmware-provided metadata order. Unknown record types fail the load, so format evolution requires synchronized driver support.

## Test Signals
Use synthetic firmware files to cover CRC mismatch, concatenated valid sections, malformed record lengths, direct-write masks, fill alignment failures, gateway timeout, metadata-only parse, board files with too many records, and valid Talyn/Sparrow firmware plus board combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/fw_inc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/interrupt.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/interrupt.c

## Purpose
`interrupt.c` owns wil6210 interrupt masking, unmasking, moderation setup, hard/threaded IRQ dispatch, HALP wake voting interrupts, firmware-ready/error handling, and IRQ registration/freeing. It supports legacy DMA and enhanced DMA as well as single MSI/INTx and triple-MSI layouts.

## Important APIs, Types, And Functions
Public entry points include `wil_mask_irq()`, `wil_unmask_irq()`, TX/RX unmask helpers, `wil_configure_interrupt_moderation()`, `wil_configure_interrupt_moderation_edma()`, `wil6210_clear_irq()`, `wil6210_set_halp()`, `wil6210_clear_halp()`, `wil6210_init_irq()`, and `wil6210_fini_irq()`. Internal handlers include legacy and EDMA RX/TX IRQ functions, `wil6210_irq_misc()`, `wil6210_irq_misc_thread()`, `wil6210_hardirq()`, and `wil6210_thread_irq()`.

## Control Flow
In single-MSI or INTx mode, the hard IRQ reads the pseudo-cause register, masks pseudo interrupts, then calls RX, TX, and MISC real handlers based on bits. RX/TX handlers mask their own source, read and clear ICR, schedule NAPI when firmware and NAPI are ready, and leave source unmasking to NAPI completion. MISC handles firmware-ready, firmware-error, mailbox, and HALP bits; firmware crash and mailbox receive are completed in thread context. In triple-MSI mode, TX, RX, and MISC have separate IRQ registrations.

## State And Persistence
The file updates `wil->status` bits such as `wil_status_irqen`, `wil_status_fwready`, and `wil_status_mbox_ready`; stores pending misc bits in `wil->isr_misc`; caches mailbox registers in `wil->mbox_ctl`; completes HALP and suspend waiters; and increments ISR counters used by debugfs. Register mask state is persistent in hardware until reprogrammed.

## Dependencies And Integration Points
It depends on register definitions in `wil6210.h`, tracepoints in `trace.h`, TX/RX NAPI handlers in `netdev.c`, WMI mailbox receive, firmware crash dump/recovery paths, platform notifications, and PM suspend synchronization. `main.c` calls clear/mask/unmask during reset and firmware load.

## Risks
IRQ ordering is delicate: real ISR registers must be masked/unmasked correctly or hardware may malfunction. Firmware error handling clears `wil_status_fwready` in hard IRQ and defers recovery/notification; races with reset and suspend need careful status checks. The debug path intentionally detects IRQs arriving while masked. Triple-MSI and pseudo-IRQ paths differ for suspend response completion.

## Test Signals
Exercise legacy DMA versus EDMA, INTx/single MSI/triple MSI, RX/TX interrupt storms, spurious zero causes, firmware-ready mailbox validation, firmware crash events, HALP vote timeouts, suspend response wakeups, and NAPI completion unmasking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/interrupt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/main.c

## Purpose
`main.c` is the central lifecycle and hardware-control file for wil6210. It defines module parameters, 32-bit MMIO copy helpers, reset/up/down flows, firmware recovery, connection teardown, TX ring allocation, broadcast ring management, private-state initialization, boot-loader interaction, firmware capability refresh, scan abort, power-save update, and HALP voting.

## Important APIs, Types, And Functions
Public functions include `wil_memcpy_fromio_32()`, `wil_memcpy_toio_32()`, `wil_mem_access_lock()`, `wil_ring_init_tx()`, `wil_bcast_init()`, `wil_bcast_fini_all()`, `wil_priv_init()`, `wil6210_disconnect()`, `wil6210_disconnect_complete()`, `wil_priv_deinit()`, `wil_refresh_fw_capabilities()`, `wil_mbox_ring_le2cpus()`, `wil_get_board_file()`, `wil_clear_fw_log_addr()`, `wil_reset()`, `wil_fw_error_recovery()`, `__wil_up()`, `wil_up()`, `__wil_down()`, `wil_down()`, `wil_find_cid()`, `wil_halp_vote()`, `wil_halp_unvote()`, and `wil_init_txrx_ops()`.

## Control Flow
The primary control path is reset. `wil_reset()` requires `wil->mutex`, blocks device memory access through `mem_lock`, aborts scans, disconnects VIFs, disables LEDs, masks/flushed IRQ/WMI/service work, resets hardware, reloads firmware and board data when requested, releases CPUs, waits for WMI ready, checks `wmi_echo()`, configures interrupt moderation, restores VIF ports, refreshes firmware-derived capabilities, and notifies platform firmware-ready. `__wil_up()` calls reset with firmware load, initializes RX/TX, sets interface type, programs MAC, enables NAPI, and requests bus bandwidth. `__wil_down()` disables NAPI/IRQ activity, stops radio operations and scans, then resets without firmware load.

## State And Persistence
The file initializes core `wil6210_priv` state: station table locks, ring metadata, mutexes, completions, workqueues, WMI queues, PM/suspend counters, EDMA defaults, aggregation limits, wake triggers, VIF limits, and recovery counters. Reset mutates firmware version, firmware capabilities, hardware status bits, station/ring state, VIF connection flags, and device registers.

## Dependencies And Integration Points
It integrates with WMI, cfg80211, netdev, TX/RX backend ops, firmware loading, boot-loader register layouts, platform operations, interrupts, PM, P2P, and debugfs recovery controls. The 32-bit IO helpers are used across firmware, mailbox, debugfs, and PMC paths.

## Risks
Reset/recovery is high blast radius. Lock ordering among `wil->mutex`, `vif_mutex`, `wmi_mutex`, `mem_lock`, NAPI synchronization, and workqueue flushes must remain consistent. Firmware recovery has retry limits and manual mode via `no_fw_recovery`. Hardware generation branches for Sparrow/Talyn/Talyn-MB must not drift. Early returns in secured-boot or load failures must release `mem_lock` and clear status bits correctly.

## Test Signals
Test cold probe reset, up/down cycles, firmware reload failures, no-flash OTP MAC paths, boot-loader MAC paths, WMI-only/debug-fw modes, firmware crash recovery, manual recovery through debugfs, scan/connect timeouts, VIF restore after reset, HALP timeout, and lockdep during concurrent suspend/remove/reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/netdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/netdev.c

## Purpose
`netdev.c` bridges wil6210 private state to Linux net_device, wireless_dev, VIF allocation, NAPI polling, open/stop behavior, netdev registration, and teardown. It keeps hardware up only while at least one interface is active.

## Important APIs, Types, And Functions
`wil_has_other_active_ifaces()` and `wil_has_active_ifaces()` implement VIF activity checks. `wil_open()` and `wil_stop()` are netdev ops. NAPI poll functions handle legacy and EDMA RX/TX completion. Allocation/registration helpers include `wil_vif_alloc()`, `wil_if_alloc()`, `wil_if_free()`, `wil_vif_add()`, `wil_if_add()`, `wil_vif_remove()`, and `wil_if_remove()`.

## Control Flow
Opening the first active interface resumes runtime PM and calls `wil_up()`. Stopping the last active interface calls `wil_down()` and releases runtime PM. `wil_if_alloc()` creates cfg80211 state, initializes private state, allocates the main station-mode VIF, and stores `radio_wdev`. `wil_if_add()` registers the wiphy, allocates a dummy NAPI netdev, binds legacy or EDMA pollers, and registers the main netdev under RTNL/wiphy locks. Removal unregisters VIFs, synchronizes NAPI before clearing VIF references, deletes timers/work, removes NAPI, and unregisters wiphy.

## State And Persistence
The file owns VIF lifetime and netdev pointers in `wil->vifs[]`, `wil->main_ndev`, `wil->napi_ndev`, and `wil->radio_wdev`. Each VIF initializes timers, work items, probe-client queues, P2P work, broadcast ring marker, and queue-stopped state. NAPI state persists until `wil_if_remove()`.

## Dependencies And Integration Points
It depends on cfg80211 initialization/deinitialization, TX/RX backend functions, ethtool setup, PM wrappers, reset/up/down in `main.c`, WMI port allocation/deletion for non-main VIFs, P2P workers, key/probe-client workers, and net queue update helpers.

## Risks
VIF removal is race-prone: cfg80211 unregister can trigger callbacks before `wil->vifs[mid]` is cleared, and NAPI may still dereference VIFs until synchronized. Open/stop assumes active-interface accounting is accurate. Dummy netdev NAPI lifetime must stay aligned with wiphy/netdev registration failure paths.

## Test Signals
Create/remove multiple VIFs while traffic is active, first-open/last-stop PM transitions, EDMA and legacy NAPI completion, connect/scan/P2P timers during VIF teardown, failure injection in wiphy/netdev registration, and RTNL/wiphy lockdep coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/netdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/p2p.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/p2p.c

## Purpose
`p2p.c` implements P2P listen/search discovery operations for 60 GHz social channel behavior. It configures firmware discovery state, coordinates scan/listen timers, reports remain-on-channel and scan completion to cfg80211, and stops radio operations during down/reset.

## Important APIs, Types, And Functions
`wil_p2p_is_social_scan()` identifies a social-channel scan. `wil_p2p_search()` configures P2P search, sets wildcard SSID and probe IEs, starts search, and arms the search timer. `wil_p2p_listen()` starts or delays remain-on-channel listen. `wil_p2p_stop_discovery()`, `wil_p2p_cancel_listen()`, `wil_p2p_listen_expired()`, `wil_p2p_search_expired()`, `wil_p2p_delayed_listen_work()`, and `wil_p2p_stop_radio_operations()` manage completion and cancellation.

## Control Flow
Search/listen operations serialize on `wil->mutex`. Listen checks for an in-progress scan under `vif_mutex`; if present, it records a pending listen and waits for delayed work. Actual start uses `wmi_p2p_cfg()`, `wmi_set_ssid()`, and either `wmi_start_listen()` or `wmi_start_search()`, then arms `discovery_timer`. Expiry work stops firmware discovery and reports cfg80211 completion. Cancellation validates the cookie, stops discovery, and sends remain-on-channel expired.

## State And Persistence
State lives in `vif->p2p`: `discovery_started`, `cookie`, `listen_chan`, `listen_duration`, `pending_listen_wdev`, timer, and work items. `wil->radio_wdev` is switched to the P2P wdev during main-MID radio operations and restored when complete.

## Dependencies And Integration Points
The file depends on WMI P2P/SSID/IE/discovery commands, cfg80211 scan and remain-on-channel APIs, timers/workqueues initialized by `netdev.c`, and scan abort/reset paths in `main.c`. It assumes lock ownership documented by `lockdep_assert_held()`.

## Risks
Search/listen and scan share VIF/radio state, so delayed listen and abort paths must avoid double completion. `wil_p2p_stop_radio_operations()` temporarily drops `vif_mutex` while stopping discovery, which requires callers to hold `wil->mutex`. Cookie mismatch and pending-listen cases need exact cfg80211 signaling to avoid userspace hangs.

## Test Signals
Run social-channel scans, listen during active scan, cancel listen with valid/invalid cookies, reset/down during P2P discovery, timer expiry for search and listen, WMI command failures, and radio_wdev restoration after every exit path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/p2p.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/pcie_bus.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/pcie_bus.c

## Purpose
`pcie_bus.c` is the PCI driver entry point for wil6210. It probes/removes hardware, maps BAR0, detects hardware generation and firmware mappings, configures DMA/IRQ mode, registers wiphy/netdev/debugfs, integrates platform operations, and wires system/runtime PM callbacks.

## Important APIs, Types, And Functions
`wil_set_capabilities()` reads JTAG/chip revision, selects Sparrow/Talyn/Talyn-MB mappings, firmware names, assert-code addresses, hardware capability bits, EDMA/reordering defaults, platform capabilities, and parse-only firmware capabilities. `wil_if_pcie_enable()` sets bus master, negotiates 3 MSI/1 MSI/INTx, initializes IRQ, and performs a reset to obtain MAC. `wil_pcie_probe()` and `wil_pcie_remove()` are driver callbacks. PM callbacks include `wil6210_suspend()`, `wil6210_resume()`, notifier handling, and runtime PM operations.

## Control Flow
Probe validates BAR size, allocates cfg80211/private/netdev state, initializes platform ops, enables PCI, requests BAR, maps CSR, detects capabilities, selects DMA mask, clears IRQs, enables the device/IRQ/reset path, registers netdev/wiphy, optionally loads WMI-only firmware for debugging, registers PM notifier, initializes debugfs, and allows runtime PM. Remove performs the reverse: PM forbid, debugfs remove, P2P/additional VIF cleanup under locks, interface removal, PCIe disable, unmap/release/disable, platform uninit, and private free.

## State And Persistence
The file stores `wil->pdev`, BAR size, CSR mapping, selected hardware name/version, firmware name, DMA address size, MSI count, platform handles/ops, platform capabilities, hardware capability bits, firmware capability parse results, and PM notifier state. Module parameters `n_msi` and `ftm_mode` influence persistent driver behavior for the module lifetime.

## Dependencies And Integration Points
It depends on PCI, runtime/system PM, platform abstraction, firmware parser, TX/RX ops selection, IRQ setup, netdev/cfg80211 registration, debugfs, reset, and PM implementation in `pm.c`. Platform ROP callbacks expose ramdump and firmware recovery to platform code.

## Risks
Probe has many rollback labels and must unwind in exact reverse order. `n_msi` is global and can be downgraded during one probe, affecting later devices. Firmware capability parsing is allowed to fail silently in `wil_set_capabilities()`, so defaults must be safe. PM paths must keep PCI bus mastering consistent with radio-on versus radio-off suspend.

## Test Signals
Probe/remove on every supported PCI ID, BAR-size rejection, DMA mask fallback, MSI downgrade from 3 to 1 to INTx, MSI-only ACPI workaround, Talyn-MB EDMA defaults, WMI-only firmware path, platform notify failures, runtime/system suspend/resume with active/inactive interfaces, and error-injection rollback coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/pcie_bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/pm.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/pm.c

## Purpose
`pm.c` implements wil6210 runtime and system suspend/resume policy. It decides whether suspend is allowed, supports radio-off suspend by bringing hardware down, supports radio-on suspend when firmware/platform capabilities allow D3 suspend, manages queues, and wraps Linux runtime PM helpers.

## Important APIs, Types, And Functions
`wil_can_suspend()` validates global and VIF-level conditions. `wil_suspend()` and `wil_resume()` dispatch to radio-on or radio-off flows. `wil_suspend_keep_radio_on()` and `wil_resume_keep_radio_on()` coordinate WMI suspend/resume while preserving connected radio state. `wil_suspend_radio_off()` and `wil_resume_radio_off()` shut hardware down/up. Runtime helpers are `wil_pm_runtime_allow()`, `wil_pm_runtime_forbid()`, `wil_pm_runtime_get()`, and `wil_pm_runtime_put()`.

## Control Flow
Suspend eligibility rejects debug/WMI-only mode, runtime suspend without platform support, active monitor/AP-like interfaces, STA/P2P client runtime suspend, connecting VIFs, reset, and recovery. Radio-on suspend stops queues, checks TX/RX/WMI idle, sends `wmi_suspend()`, waits for RX drain, masks IRQs, disables reset-on-PERST, calls platform suspend, drops bus request, and sets suspended bits. Radio-off suspend calls `wil_down()` when active, disables PCIe IRQ, and calls platform suspend. Resume reverses the chosen mode and wakes connected queues.

## State And Persistence
The file updates `wil_status_suspending`, `wil_status_suspended`, and `wil_status_resuming`; `wil->bus_request_kbps_pre_suspend`; and suspend statistics counters. Runtime PM autosuspend delay is set to one second.

## Dependencies And Integration Points
It depends on active VIF accounting from `netdev.c`, queue control helpers, TX/RX idle checks, WMI suspend/resume and idle checks, reset/up/down in `main.c`, IRQ control, bus request/platform suspend/resume hooks, and PM callbacks in `pcie_bus.c`.

## Risks
The radio-on path is sensitive to races with TX, RX, WMI events, and NAPI. It uses `down_write_trylock(&mem_lock)` to block new memory/WMI work but releases it after marking suspending; status checks must remain consistent. Failure recovery after `wmi_suspend()` attempts `wmi_resume()` and queue wake, but no-fw-recovery mode changes behavior. Counters are diagnostic and not transactional.

## Test Signals
System suspend with connected STA, runtime idle rejection for STA, monitor/AP rejection, connecting-state rejection, pending TX/RX/WMI rejection, platform suspend/resume failures, WMI resume failure with recovery, repeated suspend while already suspended, and stats updates through debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/pmc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/pmc.c

## Purpose
`pmc.c` implements the Performance Monitoring Counters capture buffer controlled through debugfs. It allocates a DMA descriptor ring and descriptor buffers, tells firmware to start/stop PMC capture with WMI commands, and exposes captured buffers/ring bytes to userspace.

## Important APIs, Types, And Functions
`struct desc_alloc_info` stores descriptor DMA address and virtual address. `wil_pmc_init()` clears and initializes `wil->pmc`. `wil_pmc_alloc()` validates descriptor count/size, allocates descriptor metadata, allocates a coherent p-ring, allocates each coherent descriptor buffer, initializes buffers with `PCM_DATA_INVALID_DW_VAL | index`, configures `vring_tx_desc` entries, and sends `WMI_PMC_ALLOCATE`. `wil_pmc_free()` optionally sends `WMI_PMC_RELEASE` and frees all coherent memory. Read APIs are `wil_pmc_read()`, `wil_pmc_llseek()`, and `wil_pmcring_read()`.

## Control Flow
All operations lock `pmc->lock`. Allocation refuses double allocation and invalid/overflowing dimensions, temporarily switches coherent DMA mask to 32-bit when the device was initialized with a wider mask because vring addresses must share upper bits, then restores the original mask. Error paths free partially allocated descriptors and ring memory. Reads map file position to descriptor index and offset, then copy from the current descriptor only; seeking clamps to PMC size.

## State And Persistence
PMC state persists in `wil->pmc`: allocation flag via `pring_va`, descriptor count/size, p-ring DMA/VA, descriptor array, and `last_cmd_status`. Captured data remains in coherent DMA buffers until freed or device teardown. `debugfs.c` frees PMC on debugfs removal/reset teardown.

## Dependencies And Integration Points
The file depends on DMA coherent allocation, WMI PMC commands, TX/RX descriptor layout, debugfs file operations declared in `pmc.h`, and the main VIF MID for WMI sends. It is controlled through debugfs `pmccfg`, `pmcdata`, and `pmcring`.

## Risks
Large descriptor counts/sizes can consume substantial coherent memory, though count and multiplication overflow are checked. The DMA mask switch assumes restoring the prior mask cannot fail. `wil_pmc_read()` only reads within a single descriptor per call, so userspace must continue reading across descriptor boundaries. Firmware release failures do not prevent memory cleanup.

## Test Signals
Test invalid dimensions, maximum ring size, allocation failure at each stage, double alloc/free without alloc, read/seek boundaries, descriptor-boundary reads, 32-bit DMA-mask systems and wider DMA-mask systems, WMI allocate/release failure, and teardown while PMC is allocated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/pmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/pmc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/pmc.h

## Purpose
`pmc.h` declares the PMC debug/capture interface shared between `pmc.c` and debugfs. It also defines the marker used to initialize unused PMC capture dwords.

## Important APIs, Types, And Functions
The header defines `PCM_DATA_INVALID_DW_VAL` and prototypes for `wil_pmc_init()`, `wil_pmc_alloc()`, `wil_pmc_free()`, `wil_pmc_last_cmd_status()`, `wil_pmc_read()`, `wil_pmc_llseek()`, and `wil_pmcring_read()`.

## Control Flow
There is no executable flow. Debugfs calls these declarations to allocate/free PMC memory, read capture data, seek within it, and dump the descriptor ring.

## State And Persistence
State is owned by `struct pmc_ctx` inside `wil6210_priv`, not by the header. The invalid dword marker is persisted into allocated coherent descriptor buffers during initialization.

## Dependencies And Integration Points
The prototypes depend on `struct wil6210_priv`, Linux `struct file`, `seq_file`, user pointers, and loff_t types. `debugfs.c` includes this header to expose PMC files.

## Risks
The header lacks an include guard in this snapshot; repeated inclusion is currently benign because it only has a macro and prototypes, but adding definitions would need a guard. Prototype users must include suitable forward declarations or headers before this file.

## Test Signals
Build coverage is the main signal: debugfs and PMC translation units should compile with this header. Runtime PMC tests are covered under `pmc.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/pmc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/rx_reorder.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/rx_reorder.c

## Purpose
`rx_reorder.c` implements software RX Block Ack reordering and ADDBA handling for wil6210, plus TX-side ADDBA initiation. It keeps 802.11 sequence-number windows ordered before passing frames to the network stack when hardware reordering is not used.

## Important APIs, Types, And Functions
Sequence helpers `seq_less()`, `seq_inc()`, `seq_sub()`, and `reorder_index()` implement 12-bit sequence arithmetic. `wil_rx_reorder()` is called from NAPI for received data. `wil_rx_bar()` processes BAR frames. `wil_tid_ampdu_rx_alloc()` and `wil_tid_ampdu_rx_free()` own reorder buffers. `wil_addba_rx_request()` responds to peer ADDBA requests and optionally allocates software reorder state. `wil_addba_tx_request()` sends originator-side ADDBA.

## Control Flow
RX reorder extracts TID/CID/MID/sequence/mcast/retry via `txrx_ops.get_reorder_params()`, finds the VIF/netdev, and locks the station TID state. Frames without reorder context are delivered immediately. Multicast duplicates are dropped by retry/last-sequence checks. Unicast frames older than the head are dropped; frames beyond the window advance the head and release stored frames; duplicate slots are dropped; in-order frames are delivered directly; out-of-order frames are buffered and contiguous frames are released.

## State And Persistence
Per-station/per-TID state lives in `wil_sta_info.tid_rx[]` as `wil_tid_ampdu_rx`: reorder buffer, starting sequence, head sequence, buffer size, stored count, first-frame adjustment flag, multicast last sequence, and drop counters. Crypto replay state is separate but displayed with this state in debugfs. ADDBA TX state is in `ring_tx_data`.

## Dependencies And Integration Points
It depends on TX/RX descriptor decoding ops, `wil_netif_rx_any()`, WMI ADDBA/DELBA response commands, station state from `main.c`, and firmware capability bits for A-MSDU/hardware reordering. Disconnect cleanup in `main.c` frees reorder contexts.

## Risks
Sequence arithmetic and window advancement are correctness-critical. Race handling around BACK establishment intentionally adjusts the first received sequence, but wrong assumptions can reorder/drop valid traffic. `wil_rx_reorder()` indexes `wil->sta[cid]` before explicit CID validation, relying on TX/RX ops to produce valid CIDs. Software buffers intentionally drop remaining frames on free to avoid delivering after socket teardown.

## Test Signals
Test in-order, out-of-order, duplicate, old, window-jump, multicast retry, first-frame mismatch, BAR release, ADDBA zero/nonzero window sizes, hardware-reordering enabled/disabled, A-MSDU capability combinations, and disconnect while reorder buffers hold frames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/rx_reorder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/trace.c

## Purpose
`trace.c` instantiates wil6210 tracepoints declared in `trace.h`. It is the single translation unit that defines `CREATE_TRACE_POINTS` for this driver.

## Important APIs, Types, And Functions
The file includes `<linux/module.h>`, defines `CREATE_TRACE_POINTS`, and includes `trace.h`. It does not define functions directly; the tracepoint machinery expands declarations from the header.

## Control Flow
There is no driver runtime control flow in this file. Build-time macro expansion creates the tracepoint definitions when tracing is enabled.

## State And Persistence
Tracepoint registration state is managed by the Linux tracing subsystem. No wil6210 runtime state is stored here.

## Dependencies And Integration Points
It depends on `trace.h` and kernel tracepoint infrastructure. Other driver files call `trace_wil6210_*()` helpers generated or stubbed by `trace.h`.

## Risks
There must be exactly one `CREATE_TRACE_POINTS` instantiation for the header. Moving this include pattern or including `trace.h` with the macro elsewhere can cause duplicate definitions.

## Test Signals
Build with `CONFIG_WIL6210_TRACING=y` and disabled. At runtime, verify wil6210 events appear in ftrace/perf only when tracing support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/trace.h

## Purpose
`trace.h` declares tracepoints for WMI commands/events, driver logs, IRQ causes, RX descriptors/status messages, TX submissions, TX completions, and EDMA TX status. It also provides empty inline stubs when wil6210 tracing is disabled or sparse checking is active.

## Important APIs, Types, And Functions
Trace event classes include `wil6210_wmi`, `wil6210_log_event`, and `wil6210_irq`. Concrete events include `wil6210_wmi_cmd`, `wil6210_wmi_event`, log levels, `wil6210_irq_pseudo`, RX/TX/MISC IRQ events, `wil6210_rx`, `wil6210_rx_status`, `wil6210_tx`, `wil6210_tx_done`, and `wil6210_tx_status`.

## Control Flow
When `CONFIG_WIL6210_TRACING` is off, the header redefines trace macros to static inline no-op functions, allowing call sites to compile without trace overhead. When tracing is enabled, it defines standard Linux trace events and includes `<trace/define_trace.h>` outside the include guard with `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE trace`.

## State And Persistence
Trace events capture transient fields from WMI headers, RX/TX descriptors, status rings, IRQ cause registers, and formatted log messages. No driver state is persisted by the header itself.

## Dependencies And Integration Points
It depends on Linux tracepoint macros, wil6210 TX/RX descriptor accessors, WMI headers, and register bit definitions. `interrupt.c`, TX/RX code, WMI code, and logging macros use the generated helpers.

## Risks
Trace events copy dynamic WMI buffers by `buf_len`; callers must pass valid buffer pointers and lengths. Any descriptor layout change must update trace field extraction. The no-op macro block must remain compatible with sparse and disabled tracing builds.

## Test Signals
Build with tracing enabled/disabled and sparse-style checking. Runtime tracing should show correct WMI IDs/MIDs, IRQ flags, RX sequence/MCS fields, and TX status fields during traffic, firmware events, and interrupt handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/trace.h -->
