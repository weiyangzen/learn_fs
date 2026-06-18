# subset-b-004964 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/sar.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/sar.c

Purpose: implements rtw89 SAR and TAS power limiting. It accepts cfg80211 SAR limits, imports ACPI SAR tables, converts power units into MAC TX-power units, and dynamically adjusts SAR through TAS based on measured transmit duty/power.

Important APIs/functions: `rtw89_query_sar()` is the main exported query path used by TX-power programming. `rtw89_ops_set_sar_specs()` is the cfg80211 set-SAR hook. `rtw89_sar_init()` loads ACPI SAR and TAS policy. `rtw89_sar_track()` periodically refreshes dynamic ACPI table selection and TAS state. `rtw89_tas_reset()`, `rtw89_tas_scan()`, `rtw89_tas_chanctx_cb()`, and `rtw89_tas_fw_timer_enable()` integrate TAS with channel, scan, MCC, and firmware timer flows.

Control flow: common SAR maps center frequencies into 2/5/6 GHz SAR subbands, handles 6 GHz spanning channels through `rtw89_get_6ghz_span()`, and chooses the minimum configured limit for spanning ranges. ACPI SAR selects a table per RF path from ACPI indicators, chooses regulation-domain entries, optionally returns path-specific values, and downgrades 2TX. Query-time TAS may add or subtract offsets for DPR off/on before conversion to MAC units.

State and persistence: `rtwdev->sar` stores active source and config; common SAR has priority over ACPI. `rtwdev->tas` stores rolling power history, ratios, thresholds, current/backup state, pause/block flags, and ACPI country policy. State is in-memory only and protected by the wiphy lock after probe.

Dependencies/integration: depends on ACPI helpers, regulatory lookup, channel context, firmware H2C TAS trigger, environment monitor TX ratio, and `rtw89_core_set_chip_txpwr()`.

Risks: incorrect unit shifts or subband mapping can over/under-limit RF power. TAS disables itself for MLD, and dynamic ACPI failure resets table selection. Rolling-average division assumes a nonzero window after reset.

Test signals: SAR debug output, cfg80211 SAR setting paths, ACPI SAR table logs, TAS debug state transitions, TX-power recalculation after SAR/TAS changes, and regulatory/channel boundary tests around 6 GHz spans.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/sar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/sar.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/sar.h

Purpose: public SAR/TAS interface for the rtw89 driver.

Important APIs/types: defines MAC TX power clamp range `RTW89_SAR_TXPWR_MAC_MIN/MAX`, `struct rtw89_sar_parm` for center frequency, TX-stream count, and optional RF-path forcing, and `struct rtw89_sar_handler` for source-specific SAR query callbacks. Exports `rtw89_sar_capa` for cfg80211 and prototypes for SAR query/printing, cfg80211 SAR application, TAS reset/scan/channel hooks, firmware timer control, init, and tracking.

Control flow/integration: consumers build `rtw89_sar_parm` and call `rtw89_query_sar()` during chip TX-power setup. Debugfs-style printers call `rtw89_print_sar()` and `rtw89_print_tas()`. mac80211 operations route set-SAR into `rtw89_ops_set_sar_specs()`.

State and persistence: this header declares interfaces only; state is carried in `struct rtw89_dev` members from `core.h`.

Dependencies: includes `core.h` for driver-wide types, RF path, ntx, channel state, and device definitions.

Risks/test signals: header/API changes affect chip TX-power code, debug output, and cfg80211 operation registration. Build tests should catch signature drift; runtime tests should confirm callers hold the wiphy lock where implementation requires it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/sar.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/ser.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/ser.c

Purpose: implements rtw89 system error recovery. It translates MAC/FW error notifications into a queued state machine that performs L1 recovery, escalates to L2 restart, captures firmware/core-dump data, and coordinates TX/RX pause/resume.

Important APIs/functions: `rtw89_ser_init()` initializes queues, flags, work items, and state tables; `rtw89_ser_deinit()` stops workers; `rtw89_ser_notify()` maps MAC error codes to SER events; `rtw89_ser_recfg_done()` completes L2 mac80211 reconfiguration. Internal state handlers cover idle, L1 pre-reset, TRX reset, HCI recovery, and L2 reset.

Control flow: notifications enqueue `ser_msg` items processed by `ser_hdl_work`. Every event runs the current state's handler; transitions emit state-out and state-in events. L1 recovery stops queues, halts DMA with HCI `mac_lv1_rcvy`, resets HCI, signals firmware M2/M4 stages, and resumes queues. Timeouts escalate to L2. L2 captures reserved PLE and firmware backtrace through indirect MAC memory reads, resets CAM/vif/mac-id state, stops core, restarts hardware with `ieee80211_restart_hw()`, then waits for reconfiguration or timeout.

State and persistence: `struct rtw89_ser` holds state, flags, message list, delayed alarm event, recovery counters, and prehandle flag. Recovery state is transient; counters persist for the device lifetime.

Dependencies/integration: mac80211 queues/restart, HCI ops, MAC error status register protocol, CAM/vif bookkeeping, power-save exit, firmware packet list cleanup, devcoredump.

Risks: message allocation under GFP_ATOMIC can fail; timeout handling can promote recoverable L1 to disruptive L2. L2 forcibly resets lists and CAM mappings, so ordering with WoWLAN/reconfig is sensitive.

Test signals: inject MAC error codes, observe SER debug state transitions, recovery counters, devcoredump availability, TX/RX queue recovery, and successful mac80211 reconfigure completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/ser.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/ser.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/ser.h

Purpose: declares the rtw89 SER lifecycle and notification interface.

Important APIs: `rtw89_ser_init()` and `rtw89_ser_deinit()` set up and tear down the recovery worker state. `rtw89_ser_notify()` is the exported path for MAC/FW error codes. `rtw89_ser_recfg_done()` is called when L2 restart reconfiguration has completed.

Control flow/integration: code that detects hardware or firmware errors includes this header to notify the SER state machine. Core restart/reconfiguration code calls the done hook to unblock L2 recovery.

State and persistence: no state is defined here; it relies on `struct rtw89_dev` and embedded `struct rtw89_ser` from `core.h`.

Dependencies: includes `core.h` for the device structure and kernel integer types.

Risks/test signals: interface drift breaks error-reporting call sites. Build coverage and simulated MAC error tests validate the declarations and event mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/ser.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/txrx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/txrx.h

Purpose: central descriptor and queue contract for rtw89 TX/RX paths across AX and BE chip generations.

Important APIs/types: rate helpers decode hardware rate fields with generation-specific masks. The file defines TX descriptor body/info bit fields, BE TXD fields, AX/BE RX descriptor fields, RX info and PHY status packed structures, TX/RX DMA channel enums, QSEL enums, and queue selector helpers `rtw89_core_get_qsel()`, `rtw89_core_get_qsel_mgmt()`, and `rtw89_core_get_tid_indicate()`.

Control flow: transmit code fills descriptor words using these masks before passing packets to HCI backends. Receive code queries chip RX descriptors and PHY status layouts using these packed structures and masks. Queue selection maps TIDs to EDCA-like hardware queues and management/high-priority channels, including MAC1-specific management queues.

State and persistence: no dynamic state; all definitions are compile-time ABI mappings to hardware/firmware descriptor layouts.

Dependencies/integration: includes debug support for warning on invalid TID use. The header is consumed by core, PCI/USB HCI, chip fill/query descriptor implementations, firmware command TX, RX parsing, and PHY statistics.

Risks: bit-field definitions are hardware ABI. A wrong mask or generation branch can corrupt TX descriptors, misparse RX status, break security CAM indexes, or route packets to wrong queues. Packed structures must match firmware DMA layout exactly.

Test signals: descriptor dump comparison against vendor specs, TX/RX across AX and BE devices, invalid TID warning paths, management queue behavior on dual-MAC devices, and RX PHY/RSSI/rate parsing validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/txrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/usb.c

Purpose: USB HCI backend for rtw89. It supplies register access, TX/RX URB handling, MAC initialization hooks, L1 recovery operations, and USB probe/disconnect integration with the shared rtw89 core.

Important APIs/functions: exported `rtw89_usb_probe()` and `rtw89_usb_disconnect()` bind/unbind a USB interface. `rtw89_usb_ops` implements `struct rtw89_hci_ops`: TX write/kickoff, register reads/writes, MAC pre/post init, resource checks, reset, and L1 recovery. Internal helpers handle vendor control requests, TX descriptor insertion, RX aggregation parsing, URB resubmission, endpoint discovery, and RX/TX queue lifecycle.

Control flow: probe allocates ieee80211 HW with USB private data, parses endpoints, initializes queues and RX URBs, initializes core/chip, registers mac80211, starts RX URBs, then marks probe done. TX pushes an rtw89 descriptor, queues the skb per channel, and `tx_kick_off` submits one bulk URB per skb. Completion strips descriptors, reports TX status or TX reports, decrements per-channel inflight counters, and frees control blocks. RX completion queues aggregate buffers to a workqueue, which splits packets by RX descriptor offsets and alignment before calling `rtw89_core_rx()`.

State and persistence: `struct rtw89_usb` holds USB device, endpoint pipes, vendor request buffer, IO error counter, RX workqueue/free queues/control blocks, anchored TX URBs, per-channel TX queues, and inflight counters. State is device-lifetime and cleared on disconnect.

Dependencies/integration: Linux USB core, mac80211 TX status/RX delivery, rtw89 chip descriptor callbacks, register definitions, HCI recovery, firmware command channel CH12.

Risks: repeated vendor/URB errors set `RTW89_FLAG_UNPLUGGED`. RX aggregation bounds and queue overflow handling are critical. CH12 firmware command mismatch is rejected. USB 512-byte multiple padding prevents transfer edge cases.

Test signals: USB2/USB3 probe, endpoint parsing, register IO, sustained aggregate RX, TX status/report delivery, disconnect while URBs are live, and SER L1 recovery toggling USB reset bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/usb.h

Purpose: private USB HCI definitions for rtw89 USB devices.

Important APIs/types: defines vendor request codes, receive buffer counts/sizes, endpoint limits, RX aggregation registers/masks, TX URB limits, `struct rtw89_usb_info` chip-specific register/endpoint mapping, RX/TX control block structures, and `struct rtw89_usb` private bus state. Declares `rtw89_usb_probe()` and `rtw89_usb_disconnect()`.

Control flow/integration: chip-specific driver modules provide `rtw89_usb_info`; `usb.c` stores it in `rtw89_usb` and uses it for MAC setup, bulk-out mapping, and aggregation alignment. `rtw89_usb_priv()` casts `rtwdev->priv` to the USB backend state.

State and persistence: `struct rtw89_usb` persists for the lifetime of the allocated ieee80211 HW and owns RX queues, free buffers, workqueue, URBs, TX queues, inflight counters, and USB endpoint state.

Dependencies: includes `txrx.h` for channel counts and descriptor symbols, and relies on Linux USB/sk_buff/workqueue types through included core headers.

Risks/test signals: array bounds depend on endpoint and DMA-channel constants. Incorrect `bulkout_id` or aggregation alignment in chip data causes TX routing or RX packet splitting failures. Probe/disconnect and module build tests validate the ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/util.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/util.c

Purpose: shared utility implementation, currently focused on dB/linear power conversion and bounded text truncation.

Important APIs/functions: `rtw89_linear_to_db_quarter()` binary-searches a large lookup table and returns the closest quarter-dBm value. `rtw89_linear_to_db()` converts to whole dBm. `rtw89_db_quarter_to_linear()` clamps a quarter-dBm input and maps it to micro-scaled linear power. `rtw89_db_to_linear()` accepts whole dBm. `rtw89_might_trailing_ellipsis()` replaces the end of a filled string buffer with `...`.

Control flow: dB conversion uses `RTW89_MIN_DBM`, `RTW89_MAX_DBM`, and a table offset so negative quarter-dBm values can index the inverse table. Out-of-range linear values clamp to min/max; between entries choose the nearest table value.

State and persistence: static immutable lookup table only; no mutable state.

Dependencies/integration: exported symbols are used by SAR/TAS rolling average power logic and potentially diagnostics. Ellipsis helper supports fixed-size debug/report buffers.

Risks: the table encodes numerical behavior; changing entries affects TAS thresholds and RF power decisions. Floating-looking macro expressions are folded into integer constants but should be handled carefully. Binary search assumes a sorted table.

Test signals: unit-style conversion checks around min/max/zero-ish values, monotonicity tests, round-trip dB-to-linear-to-dB tolerances, and debug buffer truncation cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/util.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/util.h

Purpose: shared inline helpers and utility prototypes for rtw89.

Important APIs/types: packet-number masks for CCMP/TKIP-style PN fields, `rtw89_iterate_vifs_bh()`, `rtw89_for_each_rtwvif()`, duplicate-vif guard `rtw89_rtwvif_in_list()`, signed division helpers with round-down/closest semantics, `ether_addr_copy_mask()`, `ccmp_hdr2pn()`, and prototypes for dB conversion and ellipsis helpers.

Control flow: iteration macros wrap mac80211 active-interface iteration and the driver's `rtwvifs_list`. The signed division helper normalizes negative remainders so results are mathematical floor division. `ccmp_hdr2pn()` extracts six PN bytes from an 802.11 CCMP header into a 64-bit PN.

State and persistence: no owned state; helpers inspect `rtwdev` lists and caller-provided buffers.

Dependencies/integration: includes `core.h`, depends on mac80211 iteration APIs, Ethernet address helpers, and Linux bitfield helpers. Used by SAR/TAS, WoWLAN key handling, SER/vif list safety, and diagnostics.

Risks: `rtw89_for_each_rtwvif()` requires the wiphy mutex; misuse can race list mutation. PN byte ordering is security-sensitive. Masked Ethernet copy treats each bit as a byte selector.

Test signals: lockdep for vif iteration, PN extraction vectors, negative division edge cases, and WoWLAN pattern/key tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/util.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/wow.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/wow.c

Purpose: implements rtw89 Wake-on-WLAN suspend/resume support. It selects a WoW-capable station/no-link vif, programs wake reasons and pattern CAMs, synchronizes key packet numbers and GTK/IGTK rekey state, swaps normal/WoW firmware, configures power-save and HCI/MAC state, and reports wakeup reasons to mac80211.

Important APIs/functions: `rtw89_wow_suspend()` and `rtw89_wow_resume()` are the main PM entry points. `__rtw89_wow_parse_akm()` records AKM from association requests. Internal major blocks handle cipher recognition, PN/IV conversion, key-info construction/update, AOAC report retrieval, GTK rekey notification, pattern generation, PNO offload, wake configuration, firmware swap, TRX pre/post transitions, and wake reason reporting.

Control flow: suspend parses requested wakeups, leaves normal PS, sets `RTW89_FLAG_WOWLAN`, disables normal TX/RX paths, swaps to WoW firmware, programs keep-alive/disconnect/GTK/ARP or PNO offloads, enables firmware WoW, enters PS/deep PS, and resets HCI/MAC for low power. Resume verifies WoW/power, leaves deep PS, reads wake reason, re-enables HCI/MAC, fetches AOAC reports before and after RX is ready, updates mac80211 key sequences/rekey state, disables WoW offloads, swaps back to normal firmware, restores RX filters/PPDU status, and clears wake state.

State and persistence: `rtwdev->wow` stores selected link, flags, patterns, PNO request/list, key info, GTK info, AOAC report, cipher algorithms, AKM, and counts. State is in-memory and cleared after resume/failure. Firmware maintains AOAC counters during suspend and reports them back.

Dependencies/integration: mac80211 WoWLAN/GTK APIs, cfg80211 patterns and scheduled scan, firmware H2C/C2H, CAM/security, MAC/PHY/HCI control, power-save code, util PN helpers, and chip generation callbacks.

Risks: PN/IV byte ordering and TKIP MIC swapping are security-critical. Pattern masks are translated from Ethernet to 802.11/LLC layout; off-by-one errors break wake matching. Firmware download with interrupts disabled must re-enable on failures. No-link PNO and linked WoW paths differ but share cleanup.

Test signals: suspend/resume with magic packet, disconnect, pattern, GTK rekey, PMF IGTK, and PNO; AOAC report debug logs; wakeup reason reporting; firmware swap success; key PN continuity after resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/wow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/wow.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/wow.h

Purpose: WoWLAN constants, helper types, and PM-facing declarations for rtw89.

Important APIs/types: defines PN/IPN bit masks, WoW key-info valid/symbol flags, MIC key length, firmware wake reason enum, firmware cipher algorithm enum, RSN/cipher suite structs, cipher metadata, key-iteration scratch data, security header length helper, link-state predicates, managed-feature predicate, AKM parser wrapper, and suspend/resume prototypes under `CONFIG_PM`.

Control flow/integration: TX paths call `rtw89_wow_parse_akm()` for association requests when PM is enabled. PM code calls `rtw89_wow_suspend()`/`rtw89_wow_resume()`. `rtw89_wow_get_sec_hdr_len()` supplies chip-specific security header length for older chips based on current WoW PTK algorithm.

State and persistence: declarations operate on `rtwdev->wow`; the header itself owns no state.

Dependencies: relies on `struct rtw89_dev`, vif link state, firmware enums, chip IDs, mac80211 skb/header helpers, and bitmap helpers through included project headers.

Risks/test signals: `CONFIG_PM` stubs mean non-PM builds compile out most WoW behavior. Algorithm/header-length tables must match firmware expectations. Build tests for PM and non-PM configs and WoW suspend/resume tests cover the surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/wow.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/Kconfig

Purpose: Kconfig menu for Redpine Signals/RSI wireless drivers.

Important symbols: `WLAN_VENDOR_RSI` gates the vendor menu. `RSI_91X` enables the common 91x WLAN driver and selects `BT_HCIRSI` when coexistence is enabled. `RSI_DEBUGFS` adds debugfs support. `RSI_SDIO` and `RSI_USB` enable bus-specific modules. `RSI_COEX` enables WLAN/BT coexistence and has a dependency guard against built-in RSI with modular Bluetooth.

Control flow/integration: kernel configuration uses this file to expose options under the wireless vendor tree. The Makefile consumes these symbols to include core, bus, coexistence, and debugfs objects.

State and persistence: configuration-time only; choices persist in the kernel `.config`.

Dependencies: mac80211 for core, MMC for SDIO, USB for USB, BT for coexistence.

Risks: default `m` for bus support and default `y` for debug/coex influence build coverage. Typos in help text do not affect behavior, but dependency mistakes can create invalid built-in/module link combinations.

Test signals: `allyesconfig`, `allmodconfig`, and combinations with BT built-in/modular/disabled; verify expected modules `rsi_91x`, `rsi_usb`, and `rsi_sdio`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/Makefile

Purpose: kernel build recipe for the RSI 91x driver family.

Important entries: `rsi_91x-y` lists common core objects: main, core scheduler, mac80211 glue, management, HAL, and power-save. Conditional additions include coexistence and debugfs objects. `rsi_usb-y` and `rsi_sdio-y` define bus-specific modules. `obj-$(CONFIG_RSI_91X)`, `obj-$(CONFIG_RSI_SDIO)`, and `obj-$(CONFIG_RSI_USB)` hook modules into Kbuild.

Control flow/integration: Kbuild composes `rsi_91x.o` from common objects and separate `rsi_usb.o`/`rsi_sdio.o` bus modules based on Kconfig selections.

State and persistence: build-time only.

Dependencies: names must match C source files and Kconfig symbols.

Risks/test signals: missing conditional object coverage can leave unresolved references, especially for coexistence/debugfs. Build tests across core-only, USB, SDIO, debugfs, and coex combinations validate the recipe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_coex.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_coex.c

Purpose: WLAN/Bluetooth coexistence queueing for RSI 91x devices.

Important APIs/functions: `rsi_coex_attach()` allocates the coexistence control block, initializes common/WLAN/BT queues, and starts a scheduler kthread. `rsi_coex_detach()` stops the thread, purges queues, and frees state. `rsi_coex_send_pkt()` maps HAL queues and dispatches WLAN/common packets or enqueues BT packets. `rsi_coex_recv_pkt()` handles common card-ready and sleep-notify indications.

Control flow: outbound packets are mapped from HAL queue IDs to coexistence queues. Common/WLAN packets are normally sent immediately via management/data paths; BT packets are queued and wake the coex TX thread. The scheduler repeatedly picks the last non-empty priority among common, BT, and WLAN, but only actively dequeues/sends BT packets in this file.

State and persistence: `struct rsi_coex_ctrl_block` holds queues, private common pointer, and thread event/completion state. It persists while the common driver instance is attached.

Dependencies/integration: RSI common state, HAL send functions, management handling, BT packet sender, and driver thread/event helpers. It is built only with `CONFIG_RSI_COEX`.

Risks: queue priority selection overwrites earlier choices, effectively preferring WLAN over BT over common for detection; the scheduler only services BT, so common/WLAN are handled through direct paths. Interface-down handling drops non-internal management packets with TX status.

Test signals: coex attach/detach, BT packet transmission, common card-ready handling, interface-down packet drops, and queue purging on module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_coex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_core.c

Purpose: RSI common TX queuing, WMM scheduling, station/vif lookup, and mac80211 transmit entry path.

Important APIs/functions: `rsi_core_xmit()` accepts mac80211 skbs, classifies management/control/data, prepares descriptors, starts BA sessions, applies queue watermarks, and wakes the TX thread. `rsi_core_qos_processor()` dequeues selected queues and sends packets to HAL/coex. Helpers implement weighted queue selection, TXOP-based burst counts, enqueue/dequeue, `rsi_find_sta()`, and `rsi_get_vif()`.

Control flow: beacon and management queues preempt data. Data queues use WMM weights/backoff: contending queues get `wme_params`, the minimum weight queue is selected, weights are reduced, and VO/VI may dequeue multiple packets based on TXOP duration. The processor checks hardware queue availability under `tx_lock`, wakes stopped mac80211 queues below low watermark, sends through coex or direct management/data routines, updates stats, and yields after about 300 ms of continuous work.

State and persistence: `common->tx_queue[]`, `tx_qinfo[]`, `min_weight`, `selected_qnum`, `pkt_cnt`, queue block flags, TX stats, station table, vif array, FSM state, WOW flags, and aggregation-start flags drive behavior.

Dependencies/integration: mac80211 TX metadata, RSI HAL descriptor routines, bus queue status callback, coexistence, station/vif private data, BA session API, and watermarks.

Risks: invalid vif/station lookup drops packets. Queue watermark handling must avoid deadlocking stopped mac80211 queues. `info->driver_data` shares storage with `control`, so the code copies key state before overwriting. WOW and FSM gating block TX.

Test signals: traffic across all ACs, management/EAPOL paths, AP unicast station lookup, BA session start, hardware queue full behavior, queue stop/wake watermarks, coex-enabled data path, and WOW TX blocking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_debugfs.c

Purpose: debugfs instrumentation for RSI devices.

Important APIs/functions: `rsi_init_dbgfs()` creates a per-wiphy debugfs directory and files; `rsi_remove_dbgfs()` removes it. Read handlers expose SDIO interrupt/buffer stats, LMAC firmware version, FSM/queue TX stats, and current debug-zone mask. `rsi_debug_zone_write()` updates global `rsi_zone_enabled` from a hex value.

Control flow: file operations use `single_open()` and `seq_read`. `dev_debugfs_files[]` describes file names, permissions, and fops. Initialization allocates `struct rsi_debugfs`, stores it on the adapter, creates the directory from `wiphy_name()`, and creates the requested number of entries.

State and persistence: debugfs state persists while the adapter exists. It reads live counters from `struct rsi_common` and SDIO device state, and mutates the global debug-zone mask.

Dependencies/integration: Linux debugfs/seq_file, RSI SDIO private structure, common TX stats/FSM, firmware version fields, and driver debug macro.

Risks: `sdio_stats` assumes an SDIO-shaped `adapter->rsi_dev`, so exposing it for non-SDIO adapters would be unsafe unless `num_debugfs_entries` excludes it. `debug_zone` is world-writable (`0666`) and controls global logging. `rsi_remove_dbgfs()` frees entries but not the allocated `dev_dbgfs` object in this file.

Test signals: mount debugfs, read all files on SDIO and non-SDIO builds, write debug masks, verify FSM names match `NUM_FSM_STATES`, and check cleanup on device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_hal.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_hal.c

Purpose: RSI HAL transmit descriptor construction, bus packet dispatch, beacon/BT packet formatting, and firmware boot/loading for 9113/9116 devices.

Important APIs/functions: `rsi_prepare_mgmt_desc()` and `rsi_prepare_data_desc()` prepend device descriptors to mac80211 frames. `rsi_send_data_pkt()`, `rsi_send_mgmt_pkt()`, `rsi_send_bt_pkt()`, and `rsi_send_pkt_to_bus()` dispatch frames. `rsi_prepare_beacon()` builds firmware beacon descriptors. Firmware flow is handled by `rsi_hal_device_init()`, `rsi_hal_prepare_fwload()`, `rsi_load_9113_firmware()`, `rsi_load_9116_firmware()`, bootloader command helpers, ping-pong writes, and optional flash upgrade.

Control flow: TX descriptor functions reserve frame descriptor plus extended descriptor headroom, add alignment padding, populate queue/length/rate/security/sequence/VAP/retry fields, and special-case probe responses and EAPOL. Send functions validate interface/association state, write to bus, and return TX status. Firmware init waits for bootloader readiness, selects firmware metadata by coex mode/device model, loads from request_firmware, writes via bus master operations, validates CRC or burns flash for 9113, and jumps/TA-resets for 9116.

State and persistence: uses common FSM, coex mode, firmware version fields, EAPOL confirmation state, beacon count, adapter block size, host interface ops, flash capacity, bootloader timer state, and firmware filename.

Dependencies/integration: Linux firmware loader, mac80211 frame helpers, Bluetooth skb control, RSI host interface ops, SDIO/USB differences, management/core TX paths, and Kconfig-selected coex.

Risks: descriptor headroom/alignment mistakes corrupt frames. EAPOL/probe confirmation blocks queues until firmware confirms. Firmware loading depends on exact metadata offsets, bootloader register protocol, endian handling, and timers. 9113 flash upgrade validates image address/size but writes persistent flash.

Test signals: management/data/EAPOL/beacon TX, AP/STA/P2P modes, fixed-rate config, BT data, 9113 CRC-pass and CRC-upgrade paths, 9116 chunked bootload, USB/SDIO host ops, and firmware version debugfs output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_hal.c -->
