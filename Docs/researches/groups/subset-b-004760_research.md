# subset-b-004760 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/init.c

## Purpose
`init.c` owns ath6kl hardware bring-up, firmware discovery/loading, target host-interest configuration, HTC/WMI endpoint initialization, and the stop/restart paths used by firmware recovery. It is the central transition layer between bus-specific HIF operations and the higher cfg80211/WMI runtime.

## Important APIs, Types, And Functions
The static `hw_list[]` table maps supported AR6003/AR6004 hardware versions to firmware directories, board file names, load addresses, reserved RAM sizes, UART pins, reference clocks, and workarounds. `ath6kl_init_hw_params()` selects one entry based on `ar->version.target_ver` and copies it into `ar->hw`.

Buffer/profile initialization is handled by `ath6kl_buf_alloc()`, `ath6kl_init_profile_info()`, and `ath6kl_init_control_info()`. Target setup is split across `ath6kl_configure_target()`, `ath6kl_set_htc_params()`, `ath6kl_set_host_app_area()`, and `ath6kl_target_config_wlan_params()`. Firmware retrieval is split into legacy API 1 file fetchers and `ath6kl_fetch_fw_apin()`, which parses newer firmware container IEs for firmware image, OTP, patch, capabilities, VIF count, reserved RAM, and target addresses. Upload helpers include `ath6kl_upload_board_file()`, `ath6kl_upload_otp()`, `ath6kl_upload_firmware()`, `ath6kl_upload_patch()`, `ath6kl_upload_testscript()`, and the sequencing wrapper `ath6kl_init_upload()`.

Runtime lifecycle entry points are `ath6kl_init_hw_start()`, `ath6kl_init_hw_stop()`, `ath6kl_init_hw_restart()`, and exported `ath6kl_stop_txrx()`.

## Control Flow
Startup powers on HIF, writes host-interest fields, temporarily disables target sleep, programs clock/LPO/GPIO workaround registers, uploads board/OTP/firmware/patch/testscript assets through BMI, ends BMI, waits for HTC target ready, connects WMI control and data services, starts HTC, waits for `WMI_READY`, validates ABI, writes host application area protocol version, then sends per-VIF WLAN configuration WMI commands. Error labels stop HTC, clean scatter support, and power off HIF according to progress reached.

Firmware fetch first requires a board file, optionally from exact firmware name, device-tree board-id fallback, or default board file. Testmode firmware can replace normal firmware before API container probing. API containers are tried from API5 down to API2 before falling back to API1 loose files.

## State And Persistence
Persistent state is all in memory and on target RAM/registers: `ar->hw`, `ar->fw*` image buffers, `ar->fw_api`, `ar->fw_capabilities`, `ar->vif_max`, `ar->state`, `ar->flag`, WMI endpoint maps, and host-interest fields. Firmware blobs are copied with `kmemdup()` or `vmalloc()` and retained for upload. No filesystem state is written; firmware is read through Linux firmware loading.

## Dependencies And Integration Points
This file depends on firmware loader APIs, device tree, BMI, HIF ops, HTC ops, WMI command helpers, cfg80211 VIF cleanup, debug logging, and target register constants in `target.h`. Bus backends provide HIF power, BMI, diagnostic, and scatter operations. `recovery.c` calls `ath6kl_init_hw_restart()`, while SDIO/USB remove paths call `ath6kl_stop_txrx()`.

## Risks
Risk concentrates around target-specific constants, firmware container validation, and partial-start unwind. Host-interest offsets must match firmware ABI. `ath6kl_init_get_fwcaps()` uses a suspicious bound based on `sizeof(ar->fw_capabilities) * 4`; changes to the bitmap layout should be checked carefully. `ath6kl_upload_board_file()` assumes board file sizes and target RAM addresses are consistent with hardware. Restart paths deliberately bypass outer state changes and can leave device state inconsistent if stop or start fails mid-recovery.

## Test Signals
Useful validation signals include firmware API selection logs, first-boot firmware/capability output, WMI ready wait success, ABI mismatch errors, board/OTP/patch upload failures, HTC endpoint connection failures, and successful restart after recovery. Practical tests should cover missing board files, device-tree board-id fallback, API container parse errors, testmode 1/2 firmware selection, and suspend/recovery interactions that call restart or stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/main.c

## Purpose
`main.c` is the driver’s runtime glue between firmware WMI events, cfg80211 notifications, Linux netdev operations, AP station state, multicast filters, target statistics, and diagnostic access. It does not probe hardware; it manages per-VIF behavior after core initialization.

## Important APIs, Types, And Functions
Station helpers `ath6kl_find_sta()`, `ath6kl_find_sta_by_aid()`, `ath6kl_add_new_sta()`, `ath6kl_sta_cleanup()`, and `ath6kl_remove_sta()` manage `ar->sta_list`, AP stats, WPA/WAPI IEs, power-save queues, and aggregation connection state. Cookie helpers `ath6kl_cookie_init()`, `ath6kl_alloc_cookie()`, `ath6kl_free_cookie()`, and `ath6kl_cookie_cleanup()` provide the TX context pool used by `txrx.c`.

Diagnostic functions `ath6kl_diag_read32()`, `ath6kl_diag_write32()`, `ath6kl_diag_read()`, and `ath6kl_diag_write()` wrap HIF diagnostic ops. `ath6kl_read_fwlogs()` walks the target debug log ring using host-interest addresses from `target.h`.

WMI event handlers include ready, connect, disconnect, scan complete, TKIP MIC error, target stats, wakeup, TX power, PS-Poll, and DTIM expiry processing. Netdev integration is via `ath6kl_open()`, `ath6kl_close()`, `ath6kl_set_features()`, `ath6kl_set_multicast_list()`, `ath6kl_netdev_ops`, and `init_netdev()`.

## Control Flow
Ready events populate MAC/version/capability state and wake startup waiters. Connect events notify cfg80211, update BSSID/channel, wake queues, set `CONNECTED`, reset aggregation, and adjust BSS filters. AP mode has separate BSS-start and station-association handlers that install delayed group keys, notify cfg80211 of new stations, and initialize per-station aggregation. Disconnect flow diverges by AP versus station mode: AP removes station state and cfg80211 station objects; station mode notifies cfg80211, resets aggregation, manages reconnect flags, stops queues, clears BSSID/channel, and flushes data TX.

Power-save events drive queued AP delivery: PS-Poll drains one management or data frame, DTIM expiry drains multicast PS queue, and PVB bits are updated through WMI. Multicast filter changes compare netdev multicast addresses against `vif->mc_filter`, issuing WMI add/delete commands.

## State And Persistence
All state is volatile kernel memory: station slots, AP stats, WEP/group keys stored on VIF/core structures, cookies, target stats accumulators, multicast filter list, connect flags, carrier/queue state, and firmware log snapshots. The file mutates `ar->state` indirectly only through netdev and WMI-facing behavior; persistent device configuration is pushed to firmware with WMI commands.

## Dependencies And Integration Points
Dependencies include cfg80211 notification APIs, netdev ops, WMI command/event structures, HIF diagnostic ops, target host-interest constants, aggregation helpers from `txrx.c`, and debugfw log plumbing. `init.c` waits for `ath6kl_ready_event()` effects; `txrx.c` consumes cookie and station helpers.

## Risks
Station cleanup assumes valid AID-derived array indexes; callers mostly validate AID but future paths must maintain this. AP power-save queueing and cfg80211 station notifications run across spinlocks and unlocked WMI calls; race regressions are plausible around disconnect, wake, DTIM, and removal. `ath6kl_set_features()` changes global `ar->rx_meta_ver` from per-netdev feature toggles, which matters in multi-VIF scenarios. Firmware log reading trusts target ring pointers but uses bounded loop count.

## Test Signals
Signals include cfg80211 connect/disconnect/new_sta/del_sta events, netdev carrier and queue transitions, multicast filter WMI command failures, target stats wakeups, TX power wakeups, AP max-client and ACL failure notifications, firmware log extraction, and checksum feature toggling. Stress tests should cover AP station churn, PS-Poll/DTIM delivery, multicast list changes while suspended or disconnected, and station-mode reconnect edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/recovery.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/recovery.c

## Purpose
`recovery.c` implements firmware error recovery and optional heartbeat polling. It translates endpoint-full or heartbeat failures into asynchronous hardware restart attempts and coordinates that logic with suspend/resume and driver cleanup.

## Important APIs, Types, And Functions
The core worker is `ath6kl_recovery_work()`, stored in `ar->fw_recovery.recovery_work`. Public entry points are `ath6kl_recovery_err_notify()`, `ath6kl_recovery_hb_event()`, `ath6kl_recovery_init()`, `ath6kl_recovery_cleanup()`, `ath6kl_recovery_suspend()`, and `ath6kl_recovery_resume()`. Heartbeat polling is driven by `ath6kl_recovery_hb_timer()` and WMI challenge/response commands.

## Control Flow
When an error is reported and recovery is enabled, the reason bit is recorded in `err_reason`. If cleanup is not active and the device is not already recovering, work is queued on `ar->ath6kl_wq`. The worker sets state to `ATH6KL_STATE_RECOVERY`, deletes the heartbeat timer, calls `ath6kl_init_hw_restart()`, returns state to ON, clears control endpoint full state, clears `err_reason`, and restarts heartbeat polling if configured.

Heartbeat timer ticks ignore cleanup and recovery states. Each tick checks whether the previous challenge is still pending; too many misses trigger `ATH6KL_FW_HB_RESP_FAILURE`. Otherwise it increments `seq_num`, marks a heartbeat pending, sends `ath6kl_wmi_get_challenge_resp_cmd()`, and rearms the timer. Matching heartbeat events clear `hb_pending`.

## State And Persistence
State lives in `ar->fw_recovery`: enable flag, `err_reason` bitmask, heartbeat poll interval, sequence number, miss count, pending flag, timer, and work item. The global `ar->state` and flags `RECOVERY_CLEANUP` and `WMI_CTRL_EP_FULL` are also touched. There is no persistent storage.

## Dependencies And Integration Points
This file depends on `init.c` restart, WMI challenge/response, cfg80211 stop behavior inside restart, and workqueue/timer APIs. `txrx.c` calls `ath6kl_recovery_err_notify()` when the WMI control endpoint fills.

## Risks
`ath6kl_recovery_work()` sets state back to ON even if `ath6kl_init_hw_restart()` logs failure, so later code may believe recovery succeeded. Error reasons are bit-set but cleared wholesale after the worker, which can obscure concurrent reasons. Suspend cleanup cancels work and timer, then optionally restarts inline if an error was pending; callers must ensure the device is in ON state as asserted.

## Test Signals
Useful signals include recovery debug logs, heartbeat challenge command failures, transition to and from `ATH6KL_STATE_RECOVERY`, control endpoint full clearing, timer rearm behavior, and suspend/resume with a pending `err_reason`. Fault-injection tests should simulate heartbeat misses, endpoint full, restart failure, cleanup during queued work, and resume after cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/recovery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/sdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/sdio.c

## Purpose
`sdio.c` is the SDIO HIF backend for ath6kl. It registers the SDIO driver, creates the core object, implements synchronous and asynchronous mailbox I/O, BMI transport, diagnostic window access, interrupt handling, scatter-gather support, power management, and SDIO-specific probe/remove.

## Important APIs, Types, And Functions
`struct ath6kl_sdio` holds the SDIO function, core pointer, request pools, bounce DMA buffer, scatter pool, IRQ state, async write work, and queue locks. The HIF implementation is `ath6kl_sdio_ops`.

Data movement is handled by `ath6kl_sdio_io()`, `ath6kl_sdio_read_write_sync()`, `ath6kl_sdio_write_async()`, and `ath6kl_sdio_write_async_work()`. Scatter support is handled by `ath6kl_sdio_scat_rw()`, `ath6kl_sdio_alloc_prep_scat_req()`, `ath6kl_sdio_enable_scatter()`, `ath6kl_sdio_async_rw_scatter()`, and cleanup/get/add helpers. BMI and diagnostic entry points are `ath6kl_sdio_bmi_read()`, `ath6kl_sdio_bmi_write()`, `ath6kl_sdio_diag_read32()`, and `ath6kl_sdio_diag_write32()`.

Probe/remove and PM entry points are `ath6kl_sdio_probe()`, `ath6kl_sdio_remove()`, `ath6kl_sdio_suspend()`, `ath6kl_sdio_resume()`, and empty MMC PM hooks.

## Control Flow
Probe allocates `ath6kl_sdio`, DMA buffer, request pools, work item, waitqueue, core object, HIF ops, BMI max size, and mailbox info, then configures SDIO and calls `ath6kl_core_init()` with mailbox HTC. SDIO config enables async 4-bit IRQ mode for newer devices and sets mailbox block size. Power-on enables the function, delays for hardware init, and reconfigures SDIO. Power-off disables the function.

Synchronous I/O rounds block transfers to mailbox block size, bounces unaligned or non-DMA-able buffers through `dma_buffer`, claims the SDIO host, performs fixed or incremental CMD53 access, logs/traces, and releases the host. Async writes allocate a bus request and queue work. IRQ handling releases the host before calling the HIF bottom-half handler, then reclaims it and wakes waiters.

BMI write waits for command credits then writes to mailbox. BMI read waits for RX lookahead before reading. Diagnostic access sets window address registers bytewise and then reads/writes `WINDOW_DATA_ADDRESS`.

## State And Persistence
State is volatile: SDIO enable/disable state, free request lists, async queue, scatter pool, IRQ handling flag, DMA bounce buffer, and core attachment. Firmware/module declarations are build metadata only. No disk state is written.

## Dependencies And Integration Points
The file depends on Linux MMC/SDIO APIs, ath6kl HIF/HTC/BMI/core interfaces, target register definitions, cfg80211 suspend/resume, and tracepoints. `init.c` consumes HIF power/BMI/diag/scatter ops through the generic ops table. `htc_mbox.c` uses mailbox addresses and scatter capabilities populated here.

## Risks
Async stop has comments noting work may be requeued and asserts a hard-coded scatter queue depth. Scatter virtual-buffer cleanup frees `virt_dma_buf`, which is the aligned pointer rather than necessarily the original allocation base, a pattern worth auditing. Bounce buffering serializes through one mutex-protected buffer, so long synchronous transfers can block. BMI read timeout behavior is intentionally conservative and may still be fragile on unusual controllers. Suspend fallback changes host PM flags and must preserve wake/cut-power semantics.

## Test Signals
Test signals include SDIO probe/config logs, CMD52 async IRQ enable failures, block-size setup failures, trace_ath6kl_sdio and trace_ath6kl_sdio_scat events, BMI credit/read timeouts, interrupt bottom-half status, scatter setup fallback to virtual scatter, suspend mode selection, and clean remove after active async I/O.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/target.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/target.h

## Purpose
`target.h` defines target memory/register addresses, bit masks, host-interest layout offsets, board data sizes, virtual-to-physical address macros, and debug log structures shared by ath6kl boot, diagnostic, firmware-log, SDIO, and recovery code.

## Important APIs, Types, And Constants
Board size constants distinguish AR6003 and AR6004 board and extended-board data. Register constants cover reset, CPU/system sleep, LPO calibration, GPIO pins, interrupt status/enable registers, counters, mailbox window data/address registers, scratch area, base addresses, and an analog PLL register with unknown real name.

`SM()` and `MS()` pack/unpack bitfields using matching `_S` shift constants. `struct host_interest` is a packed offset-only ABI description of the firmware host-interest area, with fields for app host area, failure state, debug log header, option flags, board data addresses, UART/refclock settings, reserved RAM, mailbox block size and yield limit, extended board data, reset flags, test app flags, testscript location, and more. `HI_ITEM()` produces offsets into that ABI.

Mode/submode constants encode firmware interface mode, P2P submode, VIF count, and bridge/MAC-address option shifts. `TARG_VTOP()` maps AR6003 virtual addresses by masking and leaves AR6004 addresses unchanged. `struct ath6kl_dbglog_buf` and `struct ath6kl_dbglog_hdr` describe firmware debug log rings.

## Control Flow
This header has no runtime flow by itself, but its constants drive flow in several files. `init.c` writes sleep, clock, GPIO, board, app-start, and host-interest fields during boot. `main.c` uses host-interest offsets and debug log structures to read firmware logs. `sdio.c` uses window and counter addresses for diagnostic access and BMI credits.

## State And Persistence
The header models persistent firmware ABI state in target RAM but stores no state itself. The most important persistence rule is structural: `struct host_interest` positions must remain stable across firmware revisions because host code computes offsets rather than sharing C instances with firmware.

## Dependencies And Integration Points
It integrates with `core.h` target type/version definitions, BMI/diagnostic operations, firmware binaries, and bus backends. Any change here can affect boot across SDIO and USB because both use the same host-interest and diagnostic abstractions.

## Risks
ABI drift is the primary risk. Reordering or resizing `struct host_interest` fields would break firmware communication. Endianness matters for debug log structures but host-interest offsets are raw 32-bit target fields. `TARG_VTOP()` returns zero for unknown target types, which can silently convert invalid target types into address zero if callers do not validate first.

## Test Signals
Validation signals are indirect: successful board upload, WMI ready event, firmware log extraction, diagnostic reads/writes, BMI mailbox credit behavior, and reset behavior. Tests should compare offsets against firmware documentation or known-good builds and exercise AR6003 versus AR6004 address conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/target.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/testmode.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/testmode.c

## Purpose
`testmode.c` implements nl80211 testmode plumbing for ath6kl. It accepts userspace test commands, forwards TCMD payloads to firmware through WMI, and emits firmware testmode events back to userspace.

## Important APIs, Types, And Functions
Local enums define netlink attributes `ATH6KL_TM_ATTR_CMD` and `ATH6KL_TM_ATTR_DATA`, commands `ATH6KL_TM_CMD_TCMD` and obsolete `ATH6KL_TM_CMD_RX_REPORT`, and a 5000-byte data limit. `ath6kl_tm_policy[]` validates command and binary payload attributes.

`ath6kl_tm_cmd()` parses a cfg80211 testmode request, requires `ATH6KL_TM_ATTR_CMD`, supports only `ATH6KL_TM_CMD_TCMD`, requires binary data, and calls `ath6kl_wmi_test_cmd(ar->wmi, buf, buf_len)`. `ath6kl_tm_rx_event()` allocates a cfg80211 testmode event skb, attaches command and payload attributes, and sends it with `cfg80211_testmode_event()`.

## Control Flow
Userspace sends a testmode netlink command to cfg80211. cfg80211 invokes ath6kl’s testmode op, which parses attributes and either forwards the payload to firmware or rejects unsupported commands. Firmware-originated testmode data is passed to `ath6kl_tm_rx_event()`, wrapped in the same command/data attribute format, and published as a cfg80211 testmode event.

## State And Persistence
This file stores no long-lived driver state. It uses `wiphy_priv()` to recover `struct ath6kl` and transient sk_buffs for event emission.

## Dependencies And Integration Points
It depends on cfg80211 testmode support, netlink attribute APIs, `ath6kl_wmi_test_cmd()`, `testmode.h`, and debug warnings. It is meaningful only when the driver was booted with testmode firmware selected in `init.c`.

## Risks
`ath6kl_tm_cmd()` does not propagate the return value of `ath6kl_wmi_test_cmd()`, so command transport failures may be invisible to userspace. Payload length is bounded by netlink policy but command semantics are firmware-defined. The obsolete RX report command is intentionally unsupported; userspace tools must use TCMD.

## Test Signals
Signals include netlink parse errors, `-EINVAL` for missing attributes, `-EOPNOTSUPP` for unknown commands, successful cfg80211 testmode events, and firmware TCMD responses. Tests should include maximum-size payloads, zero-length/missing data, unsupported commands, and event allocation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/testmode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/testmode.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/testmode.h

## Purpose
`testmode.h` provides conditional declarations for ath6kl nl80211 testmode support. It lets the rest of the driver call testmode hooks regardless of whether `CONFIG_NL80211_TESTMODE` is enabled.

## Important APIs, Types, And Functions
When testmode is enabled, it declares `ath6kl_tm_rx_event()` and `ath6kl_tm_cmd()`. When disabled, it supplies static inline no-op replacements: RX events are dropped and commands return success.

## Control Flow
The header has compile-time control flow. Enabled builds route calls to `testmode.c`; disabled builds compile out behavior without adding preprocessor checks to callers.

## State And Persistence
No state is stored. The only behavioral persistence is build configuration: disabled testmode silently discards events and treats commands as no-ops.

## Dependencies And Integration Points
It includes `core.h` for `struct ath6kl` and relies on cfg80211 types from surrounding declarations. `cfg80211.c` or related registration code can point testmode callbacks at `ath6kl_tm_cmd()` only when enabled, while WMI event handling can call `ath6kl_tm_rx_event()` unconditionally.

## Risks
Returning zero from the disabled `ath6kl_tm_cmd()` stub can hide accidental command use in builds without testmode support if the callback is reachable. Call sites should ensure userspace cannot invoke a disabled testmode op, or return `-EOPNOTSUPP` at registration boundaries.

## Test Signals
Build tests should cover both `CONFIG_NL80211_TESTMODE=y` and disabled configurations. Runtime tests in disabled builds should verify no testmode callback is exposed to userspace or that no-op behavior is intentional.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/testmode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/trace.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/trace.c

## Purpose
`trace.c` instantiates ath6kl tracepoints declared in `trace.h` and exports selected tracepoint symbols for use across ath6kl modules.

## Important APIs, Types, And Functions
The file defines `CREATE_TRACE_POINTS` before including `trace.h`, which causes Linux tracepoint infrastructure to emit definitions rather than declarations. It exports `ath6kl_sdio` and `ath6kl_sdio_scat` with `EXPORT_TRACEPOINT_SYMBOL()`.

## Control Flow
There is no runtime control flow beyond module initialization handled by the tracepoint framework. Compilation of this file materializes the tracepoint objects used by call sites.

## State And Persistence
Tracepoint state is kernel tracing infrastructure state. This file stores no driver state and no persistent data.

## Dependencies And Integration Points
It depends on Linux module and tracepoint infrastructure and on `trace.h`. SDIO tracepoints are exported because SDIO tracing may be used by separately linked objects/modules. Other tracepoints remain visible within the compilation/linking context according to normal tracepoint rules.

## Risks
Tracepoint definition files must include the trace header in exactly one C translation unit with `CREATE_TRACE_POINTS`; duplicating this pattern would cause duplicate symbols. Exporting only SDIO tracepoints means consumers expecting exported WMI/HTC/log tracepoints may fail unless linked internally.

## Test Signals
Build/link success is the primary signal. Runtime tracing can be validated by enabling ath6kl trace events under ftrace/tracefs and checking SDIO events emitted by `sdio.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/trace.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/trace.h

## Purpose
`trace.h` declares ath6kl tracepoints for WMI commands/events, SDIO transfers, SDIO scatter transfers, SDIO IRQ payloads, HTC RX/TX packets, and ath6kl logging. It also provides no-op inline trace functions when ath6kl tracing is disabled.

## Important APIs, Types, And Tracepoints
`ath6kl_get_wmi_id()` extracts a WMI command ID from a buffer when the buffer is long enough. Tracepoints include `ath6kl_wmi_cmd`, `ath6kl_wmi_event`, `ath6kl_sdio`, `ath6kl_sdio_scat`, `ath6kl_sdio_irq`, `ath6kl_htc_rx`, `ath6kl_htc_tx`, log event class instances `ath6kl_log_err`, `ath6kl_log_warn`, `ath6kl_log_info`, plus `ath6kl_log_dbg` and `ath6kl_log_dbg_dump`.

Each tracepoint records compact metadata and often a dynamic copy of the packet/buffer. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` are set so `<trace/define_trace.h>` can find this local header.

## Control Flow
When `CONFIG_ATH6KL_TRACING` is disabled, `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, and `DEFINE_EVENT` are redefined to no-op inline functions so call sites remain compilable and cheap. When enabled, standard tracepoint declarations are generated. The final include of `<trace/define_trace.h>` is intentionally outside the include guard pattern required by Linux trace headers.

## State And Persistence
Trace event records are transient kernel tracing data. The header itself stores no driver state. Dynamic arrays copy packet contents at trace time, so trace buffers may contain firmware commands, events, or network payload bytes.

## Dependencies And Integration Points
It includes cfg80211, skb, tracepoint, WMI, and HIF definitions. Call sites are in TX/RX, HTC, SDIO, and debug logging paths. `trace.c` instantiates the tracepoints.

## Risks
Dynamic buffer copies can expose sensitive payloads in trace output and can add overhead if tracing is enabled on hot data paths. The no-op fallback intentionally shadows trace macros; changes must preserve compatibility with both tracing and non-tracing builds. Tracepoint layout is a user-visible ABI for tracing tools.

## Test Signals
Tests should build with and without `CONFIG_ATH6KL_TRACING`, enable tracefs events, and verify WMI IDs, SDIO flags, scatter lengths, HTC endpoint/status, and log messages are captured without corrupting packet flow.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/txrx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/txrx.c

## Purpose
`txrx.c` implements ath6kl data/control transmit, receive processing, AP power-save queues, HTC cookie completion, RX buffer refill, A-MSDU slicing, and 802.11 aggregation reorder state. It is the primary packet data path between Linux netdev/cfg80211 state, WMI headers, HTC endpoints, and firmware.

## Important APIs, Types, And Functions
Transmit entry points are `ath6kl_control_tx()`, `ath6kl_data_tx()`, `ath6kl_tx_queue_full()`, `ath6kl_tx_complete()`, `ath6kl_tx_data_cleanup()`, and `ath6kl_indicate_tx_activity()`. AP power-save helpers include `ath6kl_powersave_ap()`, `ath6kl_process_uapsdq()`, `ath6kl_process_psq()`, and `ath6kl_uapsd_trigger_frame_rx()`.

Receive/buffer APIs include `ath6kl_rx_refill()`, `ath6kl_refill_amsdu_rxbufs()`, `ath6kl_alloc_amsdu_rxbuf()`, `ath6kl_rx()`, and `ath6kl_cleanup_amsdu_rxbufs()`. Aggregation APIs include `aggr_init()`, `aggr_conn_init()`, `aggr_recv_addba_req_evt()`, `aggr_recv_delba_req_evt()`, `aggr_reset_state()`, and `aggr_module_destroy()`.

## Control Flow
Data TX validates connected/WMI-ready/ON state, handles AP power-save queueing, prepares checksum metadata, converts Ethernet DIX to 802.3, prepends WMI data header, maps traffic to WMM AC and HTC endpoint, allocates a cookie, handles cloned unaligned skb copying, and submits asynchronously to HTC. Control TX similarly traces WMI, allocates a cookie, tracks control endpoint pressure, and submits to HTC.

TX completion walks a completed HTC packet list under `ar->lock`, validates cookies/skbs, updates pending counters and netdev stats, clears control endpoint full state, resolves the VIF by WMI interface index, returns cookies, purges skbs, wakes stopped queues, and wakes event waiters when control endpoint drains.

RX refills hand HTC aligned skbs with embedded `struct htc_packet`. `ath6kl_rx()` validates HTC status/length, dispatches control endpoint skbs to WMI, resolves VIF, updates stats, parses WMI metadata/padding, handles AP station power-save state and U-APSD triggers, removes WMI/dot11/dot3 headers, optionally loops AP intra-BSS traffic back to firmware, processes aggregation reorder for unicast traffic, and finally delivers to netif_rx.

Aggregation maintains per-TID sliding windows, queues out-of-order frames, slices A-MSDUs into MSDUs, drains in-order frames, and uses a timer to prevent held frames from remaining stuck.

## State And Persistence
State includes HTC endpoint maps, pending TX counters, cookie pool, per-VIF flags, netdev stats, IBSS endpoint/node mapping, AP per-station PS queues, multicast PS queue, A-MSDU buffer queue, aggregation hold queues/statistics/timers, and active WMM stream priority. All state is volatile.

## Dependencies And Integration Points
The file depends on WMI header conversion and pstream helpers, HTC ops, netdev APIs, cfg80211-facing VIF/station state from `main.c`, recovery notification for endpoint full, and trace/debug facilities. `init.c` wires these callbacks into HTC service endpoints.

## Risks
This is a high-concurrency hot path using spinlocks, timers, async completions, and skb ownership transfers. Cookie exhaustion drops packets. AP power-save paths intentionally return with skb consumed in some branches; future changes must preserve ownership semantics. Aggregation duplicate handling unconditionally frees any existing slot skb before replacing it, so sequence-window logic is critical. Multi-VIF checksum metadata uses global `ar->rx_meta_ver`. Queue wake/stop handling has FIXME locking comments.

## Test Signals
Signals include netdev TX/RX/drop/error counters, control endpoint full recovery, WMI/HTC tracepoints, AP PS/U-APSD queue behavior, multicast DTIM delivery, checksum offload metadata, A-MSDU slicing errors, aggregation timeout stats, ADD_BA/DEL_BA events, and queue wake/stop transitions. Stress tests should include cookie exhaustion, endpoint backpressure, cloned unaligned skbs, AP intra-BSS forwarding, reorder window wraparound, and disconnect during active traffic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/usb.c

## Purpose
`usb.c` is the USB HIF backend for ath6kl. It maps USB endpoints to ath6kl logical pipes, manages URB context pools, submits RX/TX bulk transfers, implements BMI and diagnostic vendor control messages, registers the USB driver, and connects USB devices to the common core using HTC pipe mode.

## Important APIs, Types, And Functions
`struct ath6kl_usb_pipe` stores per-pipe URB pool, anchors, endpoint descriptor, pipe handle, thresholds, completion work, and completion skb queue. `struct ath6kl_usb` stores the USB device/interface, all pipes, diagnostic buffers, core pointer, lock, and workqueue. `struct ath6kl_urb_context` binds URB completion to pipe, skb, and core.

Resource functions include `ath6kl_usb_alloc_urb_from_pipe()`, `ath6kl_usb_free_urb_to_pipe()`, `ath6kl_usb_alloc_pipe_resources()`, `ath6kl_usb_setup_pipe_resources()`, and cleanup helpers. Data path functions include `ath6kl_usb_post_recv_transfers()`, `ath6kl_usb_recv_complete()`, `ath6kl_usb_usb_transmit_complete()`, `ath6kl_usb_io_comp_work()`, `ath6kl_usb_send()`, `hif_start()`, `hif_stop()`, and `hif_detach_htc()`.

HIF ops are in `ath6kl_usb_ops`, including pipe send/map/free-queue queries, BMI read/write, diagnostic read/write, power, stop, suspend/resume stubs, and no-op scatter cleanup.

## Control Flow
Probe creates USB resources, enumerates endpoint descriptors into logical pipes, allocates the common core, sets HIF type/ops, mailbox block size and BMI max size, then initializes core in HTC pipe mode. `hif_start()` posts RX transfers and sets TX thresholds. RX completion queues received skbs to pipe work and reposts URBs when enough free contexts accumulate. TX completion returns the URB context to the pool and queues skb completion work. The work item calls `ath6kl_core_rx_complete()` or `ath6kl_core_tx_complete()` depending on pipe direction.

Service mapping sends WMI control on TX control and data down RX data, maps BE/BK to low-priority TX, maps VI/VO to low- or medium-priority TX based on firmware capability, and uses RX data for receive. BMI and diagnostic operations use vendor control requests rather than mailbox CMD53.

Disconnect stops TX/RX, waits briefly for target reboot, cleans up core, kills anchored URBs, flushes work, frees pipe resources, buffers, workqueue, and USB object.

## State And Persistence
State is volatile: endpoint/pipe mappings, URB context counts, submitted anchors, completion queues, diagnostic buffers, and workqueue. Module firmware declarations are metadata. USB autosuspend support is declared but cfg80211 suspend/resume hooks are stubs.

## Dependencies And Integration Points
It depends on Linux USB APIs, ath6kl core and pipe-mode HTC, WMI service IDs, firmware capability bits, and core RX/TX completion handlers. Unlike SDIO, it does not support scatter and does not use mailbox BMI credits.

## Risks
URB pool exhaustion returns `-ENOMEM` and can occur if multiple endpoints map to one pipe, as noted by TODO. Completion work uses skbs as completion tokens, so ownership must remain exact across submit failures, disconnect, and flush. `ath6kl_usb_diag_read32()` sends the size of the write diagnostic command for read requests, which appears intentional for fixed command buffer size but should be verified against firmware. USB suspend only flushes I/O and PM resume reposts RX data/data2 without full cfg80211 resume support.

## Test Signals
Signals include USB probe endpoint logs, pipe resource counts/leak warnings, RX/TX completion logs, URB submit failures, vendor control request failures, core init result, disconnect cleanup without URB leaks, pipe free queue counts under load, and resume repost behavior. Tests should cover high-rate TX/RX, disconnect during active URBs, BMI/diag request failures, endpoint descriptor variants, and firmware capability changes in pipe mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/usb.c -->
