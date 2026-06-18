# subset-b-004841 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54spi_eeprom.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54spi_eeprom.h

Purpose: this header embeds a static Prism54 SPI EEPROM/PDA image as `p54spi_eeprom[]`. It is not executable logic; it is calibration and identity data used by the p54 SPI path when a device lacks a usable external EEPROM image.

Important data: the byte array starts with an `eeprom_pda_wrap`-style magic header, a placeholder MAC address, interface list data, hardware platform component ID, country list/default country, antenna gain, RSSI approximation, PA calibration curves, ZIF TX IQ calibration entries for 2.4 GHz channels, and a `PDR_END` marker. Comments identify PDA records such as `PDR_MAC_ADDRESS`, `PDR_INTERFACE_LIST`, `PDR_COUNTRY_LIST`, `PDR_PRISM_PA_CAL_CURVE_DATA_CUSTOM`, and `PDR_PRISM_ZIF_TX_IQ_CALIBRATION`.

Control flow and state: there are no functions, locks, or runtime state transitions in this file. Persistence behavior is the static in-kernel copy of factory-like EEPROM data; downstream parser code treats this byte stream as if it were read from device EEPROM.

Dependencies and integration: it is protected by `P54SPI_EEPROM_H` and depends on p54 EEPROM/PDA parsers elsewhere to interpret record lengths and IDs correctly. Regulatory and RF calibration behavior depends on consumers preserving the byte ordering and record boundaries.

Risks: the embedded MAC is explicitly bogus, so callers must replace or tolerate it. The large calibration table is brittle: accidental byte edits, truncation, endian assumptions, or record length mismatches can silently damage RF behavior. Test signals are compile inclusion, successful p54 EEPROM parse, expected country/channel registration, and functional TX power/RSSI behavior on SPI Prism54 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54spi_eeprom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54usb.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54usb.c

Purpose: this is the USB transport driver for Prism54/p54 devices. It binds a large USB ID table, detects either ISL3887 direct USB hardware or ISL3886 behind a NET2280 bridge, loads firmware, uploads it through the appropriate boot path, wires URB RX/TX callbacks to the common p54 mac80211 core, and registers/unregisters the common wireless device.

Important APIs and functions: module metadata advertises `isl3886usb` and `isl3887usb` firmware. `p54u_probe()` allocates `ieee80211_hw` via `p54_init_common()`, identifies endpoint layout, chooses `p54u_tx_lm87()` or `p54u_tx_net2280()`, and starts async firmware loading with `p54u_load_firmware()`. `p54u_start_ops()` parses firmware, validates firmware interface, uploads firmware, starts URBs, reads EEPROM, stops, then calls `p54_register_common()`. RX is handled by `p54u_rx_cb()`, which adjusts transport headers and calls `p54_rx()`. TX completion uses `p54u_tx_cb()` to call `p54_free_skb()`.

Control flow: probe initializes queues/anchors and schedules firmware. The firmware callback calls `p54u_start_ops()`, and on failure releases the USB interface. Open/stop only manage RX URBs because the code comments say reliable hardware stop is not known. Reset/resume re-upload firmware and restart mac80211 state when needed.

State and persistence: `struct p54u_priv` stores the USB device/interface, firmware pointer, selected hardware type, upload callback, RX skb queue, submitted URB anchor, and completion for async firmware load. Firmware blobs are retained until disconnect. URB lifetime is anchored under `priv->submitted`.

Dependencies and integration: this file depends on USB core, firmware loader, PCI/NET2280 constants, `p54.h`, `lmac.h`, `p54usb.h`, and common p54 functions. Hardware-facing dependencies include bulk endpoints, interrupt endpoint behavior, NET2280 register access, CRC32 framing for ISL3887 X2 upload, and p54 firmware interface IDs.

Risks and tests: firmware upload paths are timing-sensitive and use fixed sleeps, CRC handshakes, DMA status bits, and endpoint heuristics. RX buffer reuse depends on `p54_rx()` returning whether the skb was consumed. Test signals include device probe for both endpoint layouts, firmware load failures, suspend/resume/reset, URB leak checks, EEPROM read success, and packet TX/RX through mac80211.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54usb.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54usb.h

Purpose: this header defines the USB-specific protocol, hardware constants, transfer headers, register access packets, endpoint IDs, firmware upload header, and private state for `p54usb.c`.

Important types and constants: NET2280 PCI/GPIO/register macros describe the bridge setup path for version 1 devices. `struct net2280_tx_hdr` and `struct lm87_tx_hdr` are transport headers prepended before p54 frames. `enum net2280_op_type`, `struct net2280_reg_write`, and `struct net2280_reg_read` encode register transactions over bridge/device bulk endpoints. `struct x2_header` supports ISL3887 firmware upload. `enum p54u_pipe_addr` names data, management, bridge, device, and interrupt pipes. `enum p54u_hw_type` distinguishes invalid, NET2280, and 3887 hardware. `struct p54u_priv` embeds `struct p54_common` and adds USB, firmware, queue, anchor, and completion state.

Control flow and state: no functions live here, but the fields control the driver lifecycle: `upload_fw` selects the boot path, `rx_queue` and `submitted` manage URB lifetime, `fw` persists the requested firmware, and `fw_wait_load` synchronizes disconnect with the async firmware callback.

Dependencies and integration: it includes `p54pci.h` for ISL3886 register definitions and `<linux/usb/net2280.h>` for bridge bit positions. It is tightly coupled to `p54usb.c`, `p54_common`, USB URBs, and firmware loader behavior.

Risks and tests: packed struct layout and endian fields are hardware ABI. Incorrect pipe numbers, header sizes, or register constants can break firmware upload or data transfer. Build tests should catch missing definitions; runtime tests should verify endpoint detection, both TX header formats, reset/resume, and successful p54 common registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/p54usb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/txrx.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/txrx.c

Purpose: this is common Prism54 mac80211 TX/RX handling shared by p54 transports. It translates mac80211 skbs into p54 firmware frames, manages firmware RAM address allocation for outstanding TX frames, processes RX data/control frames, accounts queue pressure, updates survey/statistics, and reports TX status back to mac80211.

Important functions: `p54_tx_80211()` builds p54 data headers, ratesets, retry counts, crypto metadata, padding, and queue/backlog values before calling `p54_tx()`. `p54_assign_address()` reserves firmware memory windows and sets `req_id`. `p54_free_skb()` and `p54_find_and_unlink_skb()` release outstanding TX state. `p54_rx()` dispatches data versus control frames. `p54_rx_data()` builds `ieee80211_rx_status` and calls `ieee80211_rx_irqsafe()`. `p54_rx_frame_sent()` maps firmware TXDONE into mac80211 TX status. `p54_rx_stats()` updates noise and survey counters. `p54_rx_eeprom_readback()` and trap handling complete firmware command side effects.

Control flow: outgoing frames are queued in `tx_pending`, allocated into firmware RAM in address order under `tx_queue.lock`, and passed to the transport `priv->tx`. Firmware TXDONE returns the same `req_id`, allowing lookup and status completion. Incoming data frames are validated for FCS and mode, trimmed to 802.11 payload, then handed to mac80211. Control frames update EEPROM/stat completions, beacon loss/rfkill traps, or TX completion.

State and persistence: key mutable state includes `tx_queue`, `tx_pending`, per-queue `tx_stats`, `beacon_req_id`, EEPROM/stat completions, TSF high/low tracking, survey raw counters, power-save override, and current RSSI conversion data. State persists only in driver memory and is protected by spinlocks where shared with interrupt/URB contexts.

Dependencies and integration: depends on mac80211, p54 LMAC structures, transport callbacks, firmware memory layout (`rx_start`/`rx_end`), and common p54 configuration. Crypto handling depends on mac80211 key metadata and p54 firmware expectations for WEP/TKIP/CCMP.

Risks and tests: address allocator fragmentation and 32-entry limits can stall TX. `skb->cb` reuse for driver data is order-sensitive. TKIP IV/MIC mutation must be reversed for TX status. Test signals include saturated queue behavior, TXDONE matching, beacon queue completion, RX FCS/decrypt flags, scan/stat completions, power-save beacon TIM workaround, and survey counter sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/Kconfig

Purpose: this vendor Kconfig menu gates Marvell wireless driver choices. `WLAN_VENDOR_MARVELL` is a boolean menu selector defaulting to yes; when enabled it sources Libertas, Libertas thin firmware, and mwifiex Kconfig files and defines the `MWL8K` PCI/PCIe mac80211 driver option.

Important symbols: `WLAN_VENDOR_MARVELL` controls menu visibility only. `MWL8K` is tristate, depends on `MAC80211 && PCI`, and builds the `mwl8k` module for Marvell TOPDOG 88W8xxx PCI/PCIe devices.

Control flow and integration: Kconfig flow is declarative. If the vendor selector is disabled, downstream Marvell driver options are hidden. If enabled, child Kconfig files contribute bus-specific and family-specific symbols. The matching `Makefile` consumes these symbols to include subdirectories or objects.

State and persistence: selections persist in the kernel `.config`, not in runtime driver state.

Dependencies and risks: incorrect dependencies can expose unbuildable drivers or hide valid hardware support. The top-level selector intentionally does not affect compiled code by itself. Test signals are Kconfig menu visibility, `allmodconfig`/`randconfig` coverage, and verifying selected symbols produce expected objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/Makefile

Purpose: this Makefile maps Marvell wireless Kconfig symbols to build outputs.

Important entries: `obj-$(CONFIG_LIBERTAS) += libertas/`, `obj-$(CONFIG_LIBERTAS_THINFIRM) += libertas_tf/`, `obj-$(CONFIG_MWIFIEX) += mwifiex/`, and `obj-$(CONFIG_MWL8K) += mwl8k.o`.

Control flow and integration: kbuild descends into subdirectories or compiles `mwl8k.o` based on the resolved `.config`. It is paired with `marvell/Kconfig`; each symbol must be declared there or in sourced children.

State and persistence: no runtime state. Build inclusion is determined by kernel configuration.

Risks and tests: symbol/name drift causes missing modules or dead build rules. Test signals are `make M=drivers/net/wireless/marvell`, `allmodconfig`, and verifying module names match help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/Kconfig

Purpose: this Kconfig file declares the Libertas 8xxx driver core and USB/SDIO/SPI bus frontends.

Important symbols: `LIBERTAS` is the core tristate and depends on at least one bus family (`USB || MMC || SPI`) plus `CFG80211`; it selects `FW_LOADER`. `LIBERTAS_USB`, `LIBERTAS_SDIO`, and `LIBERTAS_SPI` depend on the core and their respective bus subsystems. `LIBERTAS_DEBUG` enables debug output, and `LIBERTAS_MESH` enables mesh support.

Control flow and integration: these options drive `libertas/Makefile`, where the core object is built from common files and bus objects are added as separate modules. Mesh support conditionally adds `mesh.o` and exposes mesh-related callbacks in cfg80211/ethtool paths.

State and persistence: configuration persists in `.config`. Runtime effects include debug macros becoming active under `CONFIG_LIBERTAS_DEBUG` and mesh structures/code being compiled only when `CONFIG_LIBERTAS_MESH` is set.

Risks and tests: dependency mistakes can allow a bus driver without the shared core or firmware loader. Test signals are Kconfig dependency resolution, build coverage for each bus combination, and module autoload behavior with firmware present/missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/Makefile -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/Makefile

Purpose: this Makefile assembles Libertas common and bus-specific modules.

Important entries: the `libertas-y` composite includes `cfg.o`, `cmd.o`, `cmdresp.o`, `debugfs.o`, `ethtool.o`, `main.o`, `rx.o`, `tx.o`, and `firmware.o`, with `mesh.o` added under `CONFIG_LIBERTAS_MESH`. Bus composites are `usb8xxx-objs += if_usb.o`, `libertas_cs-objs += if_cs.o`, `libertas_sdio-objs += if_sdio.o`, and `libertas_spi-objs += if_spi.o`. Final `obj-*` rules build the core and selected bus modules.

Control flow and integration: kbuild links shared core code into `libertas.o`; bus modules depend on exported core functions and register actual hardware transports.

State and persistence: no runtime state. The build graph determines which objects exist.

Risks and tests: missing common objects would surface as unresolved symbols in bus modules. Mesh conditionality must match C preprocessor guards. Test signals are per-symbol module builds and checking that selected frontends can link against `libertas.o`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cfg.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cfg.c

Purpose: this file implements cfg80211 support for Libertas. It exposes wiphy capabilities, scans, connect/disconnect, key management, IBSS, interface mode changes, power management, regulatory handling, and allocation/registration/freeing of `wireless_dev`.

Important APIs and functions: static 2.4 GHz channel/rate tables and `cipher_suites` describe hardware capability. TLV builders such as `lbs_add_ssid_tlv()`, `lbs_add_channel_list_tlv()`, `lbs_add_supported_rates_tlv()`, `lbs_add_common_rates_tlv()`, `lbs_add_auth_type_tlv()`, `lbs_add_wpa_tlv()`, and `lbs_add_wps_enrollee_tlv()` assemble Marvell command payloads. `lbs_cfg_scan()` starts delayed scan work; `lbs_ret_scan()` parses firmware scan responses and calls `cfg80211_inform_bss()`. `lbs_cfg_connect()`, `lbs_associate()`, `lbs_disconnect()`, and cfg80211 key callbacks map userspace requests to firmware commands. IBSS is handled by `lbs_join_ibss()`, `lbs_ibss_join_existing()`, `lbs_ibss_start_new()`, and `lbs_join_post()`. Registration is through `lbs_cfg_alloc()`, `lbs_cfg_register()`, `lbs_scan_deinit()`, and `lbs_cfg_free()`.

Control flow: scans are chunked by `LBS_SCAN_BEFORE_NAP` to avoid staying off-channel too long, stop carrier/queue while scanning, submit `CMD_802_11_SCAN`, and reschedule until channels are exhausted. Connect optionally performs an internal scan, finds a BSS, clears old WEP state, configures WEP/WPA/RSN/authtype/radio, sends associate, and reports `cfg80211_connect_result()`. Disconnect sends deauthenticate and updates cfg80211/netif state. IBSS either joins a scanned BSS or starts a new one and fabricates IEs for cfg80211.

State and persistence: it mutates `lbs_private` fields including `scan_req`, `scan_channel`, `internal_scan`, `assoc_bss`, WEP key cache, `mac_control`, `connect_status`, `country_code`, `psmode`, and wiphy registration state. State is in-memory; firmware holds mirrored keys, association, channel, RSN, and power-save settings.

Dependencies and integration: depends on cfg80211, netdev queues/carrier, Libertas command helpers in `cmd.c`, host TLV definitions, mesh helpers, and `work_thread`. It is the main bridge between nl80211 userspace and firmware commands.

Risks and tests: scan response parsing trusts firmware lengths after validation and must not overrun TLV data. Internal connect waits can time out without explicit scan failure propagation. Key index and WEP/TKIP handling are firmware-specific. Test signals include `iw scan`, WPA/WEP/open association, no-BSSID connect, disconnect events, IBSS join/start/leave, monitor/mesh restrictions, regulatory hints, and power-save enable/disable on interrupt versus polling devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cfg.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cfg.h

Purpose: this header declares the cfg80211-facing Libertas helpers exported from `cfg.c` to the rest of the driver.

Important APIs: allocation/registration/free are `lbs_cfg_alloc()`, `lbs_cfg_register()`, and `lbs_cfg_free()`. Event helpers are `lbs_send_disconnect_notification()` and `lbs_send_mic_failureevent()`. Scan lifecycle is `lbs_scan_done()` and `lbs_scan_deinit()`. Link teardown is `lbs_disconnect()`.

Control flow and integration: bus/core startup code allocates a `wireless_dev` before firmware details are known, then calls registration once firmware capability/region data are available. Command response/event paths use the notification helpers to report firmware events to cfg80211. Shutdown calls scan deinit/free to cancel work and unregister wiphy.

State and persistence: declarations operate on `struct lbs_private` and its `wdev`, scan, and association state. No state is defined in the header.

Risks and tests: prototypes must stay synchronized with cfg.c and callers. Test signals are successful link of core/bus modules and correct cleanup during probe failure, disconnect, and module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cmd.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cmd.c

Purpose: this is the Libertas firmware command engine and command helper library. It builds common firmware commands, owns the fixed command buffer pool, queues and submits commands to the bus `hw_host_to_card` hook, handles synchronous waits/asynchronous callbacks, and coordinates power-save/deep-sleep constraints.

Important functions: command helpers include `lbs_update_hw_spec()`, `lbs_host_sleep_cfg()`, `lbs_set_ps_mode()`, `lbs_cmd_802_11_sleep_params()`, `lbs_set_deep_sleep()`, `lbs_set_host_sleep()`, `lbs_set_snmp_mib()`, `lbs_get_tx_power()`, `lbs_set_monitor_mode()`, `lbs_set_channel()`, `lbs_update_channel()`, `lbs_get_rssi()`, `lbs_set_11d_domain_info()`, `lbs_get_reg()`, `lbs_set_reg()`, `lbs_set_radio()`, and MAC control helpers. Queue/core APIs are `lbs_allocate_cmd_buffer()`, `lbs_free_cmd_buffer()`, `lbs_execute_next_command()`, `__lbs_cmd_async()`, `lbs_cmd_async()`, `__lbs_cmd()`, `lbs_complete_command()`, and `lbs_ps_confirm_sleep()`.

Control flow: callers allocate a free `cmd_ctrl_node`, copy the command into its 2 KiB buffer, set command/size/result, queue it, and wake the main thread. `lbs_execute_next_command()` enforces single in-flight `cur_cmd`, power-save wake rules, and optional return to PS mode when idle. `lbs_submit_command()` stamps a sequence number, calls `hw_host_to_card(MVMS_CMD, ...)`, and arms a timeout except for deep sleep. Responses are completed by `cmdresp.c`.

State and persistence: `lbs_private` stores `cmd_array`, `cmdfreeq`, `cmdpendingq`, `cur_cmd`, `seqnum`, `dnld_sent`, timers, sleep/host-sleep flags, firmware release/capability/region/MAC address, and country code. State is volatile, with selected settings mirrored into firmware.

Dependencies and integration: depends on host command structs, cfg80211 wiphy/channel data for 11d, netdev state for monitor mode, wait queues, timers, kfifo state, and bus-specific hardware send callbacks. It exports command functions used by cfg80211, debugfs, ethtool, main, and bus code.

Risks and tests: command queue correctness depends on locks, list membership, and one in-flight command. Power-save ordering is subtle: non-PS commands may trigger EXIT_PS instead of immediate submission. Deep sleep rejects commands until wake. Test signals include command timeout/retry behavior, concurrent synchronous commands, suspend/resume signals, scan/associate longer timeout paths, register debugfs access, and firmware version/region parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cmd.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cmd.h

Purpose: this header defines the command control node and prototypes/macros for Libertas firmware command submission and response/event processing.

Important types and APIs: `struct cmd_ctrl_node` holds list linkage, result, callback and argument, command buffer pointer, and a wait queue flag for synchronous commands. `lbs_cmd()` wraps `__lbs_cmd()` while preserving the caller's original response buffer size; `lbs_cmd_with_response()` uses `lbs_cmd_copyback()`. Prototypes cover async and sync command submission, buffer allocation/free, command execution/completion, response processing, event processing, and specific command helpers for channel, power save, host sleep, radio, MAC control, SNMP, monitor mode, RSSI, 11d, register access, and hardware spec.

Control flow and integration: most driver code includes this header to send firmware commands without knowing queue internals. `cmdresp.c` uses the response/event declarations; cfg/debugfs/ethtool use specific helper prototypes.

State and persistence: the header defines no storage, but `cmd_ctrl_node` instances are allocated by `cmd.c` and stored in `lbs_private`. Callback and wait queue fields determine whether command state is recycled immediately or after synchronous waiters inspect results.

Risks and tests: the `lbs_cmd()` macro temporarily overwrites `hdr.size` with `sizeof(*cmd)` while passing the original expected copyback size; misuse with non-standard command buffers can copy too much or too little. Test signals are compile coverage across all callers and command/response size sanity under firmware interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cmdresp.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cmdresp.c

Purpose: this file handles firmware command responses and asynchronous firmware events for Libertas.

Important functions: `lbs_process_command_response()` validates that a response matches `priv->cur_cmd` by sequence and command ID, handles firmware defer/error/PS special cases, invokes the command callback, completes the command, and clears the timeout. `lbs_process_event()` maps firmware event IDs to driver actions. `lbs_mac_event_disconnected()` reports disconnect, stops queues/carrier, frees current TX skb, resets link state, and exits power save if needed.

Control flow: bus code stores responses in `resp_buf` and notifies the main thread, which calls this response processor. For normal successful commands, the callback runs outside `driver_lock` but under `priv->lock`, then completion returns the node to the free queue or wakes a synchronous waiter. PS mode responses update `psstate`/`needtowakeup` inline. Events handle deauth/disassoc/link lost, PS sleep/awake, host/deep sleep wake, MIC failures, MIB/init notifications, RSSI/SNR threshold events, and mesh autostart.

State and persistence: it mutates `connect_status`, `tx_pending_len`, `currenttxskb`, `psstate`, `needtowakeup`, `is_deep_sleep`, `is_host_sleep_activated`, command timer state, and command queue state. No persistent storage is used.

Dependencies and integration: depends on cfg80211 notification helpers, command completion from `cmd.c`, netdev queue/carrier APIs, firmware event constants, wait queues, and bus/main-thread delivery of responses/events.

Risks and tests: mismatched sequence/command responses leave errors and can stall command progress. Firmware result `0x0004` intentionally lets commands time out and resubmit, so timeout handling must be tested. The disconnect path sleeps for supplicant compatibility. Test signals include invalid response injection, PS enter/exit events, host/deep sleep wake events, MIC failure reporting, link-loss notifications, and command callback execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/cmdresp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/debugfs.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/debugfs.c

Purpose: this file creates Libertas debugfs control/status files under `lbs_wireless/<netdev>/`. It exposes device info, sleep parameters, host sleep, firmware event subscriptions, raw MAC/BBP/RF register access, and optional debug fields when `PROC_DEBUG` is enabled.

Important APIs and functions: global lifecycle is `lbs_debugfs_init()`/`lbs_debugfs_remove()`, while per-device lifecycle is `lbs_debugfs_init_one()`/`lbs_debugfs_remove_one()`. File handlers include `lbs_dev_info()`, sleep parameter read/write, host sleep read/write, `lbs_threshold_read()`/`lbs_threshold_write()` for RSSI/SNR/fail/beacon events, register read/write handlers for MAC/BBP/RF, and optional `lbs_debugfs_read()`/`lbs_debugfs_write()` for selected `lbs_private` fields.

Control flow: init creates a root directory, per-device directory, base files, `subscribed_events`, and `registers`. Reads allocate one page, issue command helpers where needed, format values, and copy to userspace. Writes parse user input with `sscanf()`/`simple_strtoul()`, then issue firmware commands or update offsets. Event subscription writes first read current subscription state, update a mask, build one TLV, and write it back.

State and persistence: debugfs state is in dentries stored in `lbs_private`; actual settings affect firmware (`CMD_802_11_SLEEP_PARAMS`, host sleep, subscribe events, register writes) or driver offsets (`mac_offset`, `bbp_offset`, `rf_offset`). State is not persistent across driver reloads.

Dependencies and integration: depends on debugfs, command helpers in `cmd.c`, host TLV structs, `lbs_private`, and netdev names. It is diagnostic but can materially change hardware behavior.

Risks and tests: raw register writes are privileged and hazardous. Parser bounds rely on page-sized `memdup_user_nul()` limits. Optional debug `items[]` mutates stored offsets by adding `priv`, so multiple init paths would be risky. Test signals include debugfs tree creation/removal, valid/invalid writes, firmware command failures, register read/write behavior, and module unload without dangling dentries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/debugfs.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/debugfs.h

Purpose: this header declares the Libertas debugfs lifecycle entry points.

Important APIs: `lbs_debugfs_init()` and `lbs_debugfs_remove()` manage the global root. `lbs_debugfs_init_one()` and `lbs_debugfs_remove_one()` manage per-device files using `struct lbs_private` and `struct net_device`.

Control flow and integration: module/core init calls the global initializer; device add/remove paths call the per-device functions. Removal order should mirror creation to avoid stale dentries.

State and persistence: no state is defined here. Dentry pointers live in `lbs_private` and in `debugfs.c`'s global root.

Risks and tests: prototypes must remain aligned with `debugfs.c` and main/core callers. Test signals are build coverage with debugfs enabled and clean device/module teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/decl.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/decl.h

Purpose: this shared declaration header connects Libertas source files without pulling in all implementation headers.

Important types and APIs: `struct lbs_fw_table` maps card models to helper/main firmware names. `lbs_fw_cb` is the async firmware completion callback type. The header declares ethtool ops, TX/RX entry points, card lifecycle (`lbs_add_card()`, `lbs_remove_card()`, `lbs_start_card()`, `lbs_stop_card()`), interface lifecycle/type changes, multicast, suspend/resume, event/command response notifiers, rate conversion, and firmware loading helpers.

Control flow and integration: bus drivers use card and firmware helpers; core main code uses TX/RX and cfg/command declarations; firmware loading callbacks return helper/main firmware to bus-specific setup. This header is a central dependency for `dev.h`, `cmd.c`, `cfg.c`, `firmware.c`, and bus frontends.

State and persistence: no state is defined. Firmware table entries are normally static const arrays in bus code; returned firmware references must be released by callers according to the API.

Risks and tests: broad declaration headers can hide dependency cycles and stale prototypes. Test signals are full Libertas build across USB/SDIO/SPI and firmware load paths for one-stage and two-stage devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/decl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/defs.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/defs.h

Purpose: this header centralizes Libertas constants, debug macros, firmware capability bits, buffer sizes, radio/mesh/security constants, and core enums.

Important definitions: debug masks and `lbs_deb_*` macros are active under `CONFIG_LIBERTAS_DEBUG`. Buffer and protocol constants include command buffer counts/sizes, upload sizes, multicast limits, channel/rate limits, EEPROM/TX/RX packet sizing helpers, WOL criteria/rules, mesh IE values, firmware version macros, TX/RX descriptor flags, key lengths/types, band/rate constants, and default FWT values. Enums define SNR/NF selection, power modes, PS states, download states, media state, privacy filter, message type, key type, and WPA key info flags.

Control flow and integration: code throughout Libertas uses these macros to size allocations, parse firmware capabilities, decide power-save transitions, build mesh/crypto commands, and emit debug output. `extern unsigned int lbs_debug`, `lbs_driver_version`, and `lbs_region_code_to_index` are provided by other compilation units.

State and persistence: no storage except extern declarations. Values become compile-time constants or runtime flags in other files.

Risks and tests: changing sizes or enum values affects firmware ABI and buffer safety. Debug macros must compile away cleanly without debug config. Test signals include compile with and without `CONFIG_LIBERTAS_DEBUG`/`MESH`, command buffer stress, WOL option mapping, and firmware version/capability handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/dev.h -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/dev.h

Purpose: this header defines `struct lbs_private`, the central per-device state object for the Libertas driver, plus related sleep and mesh stats structures.

Important types: `struct sleep_params` mirrors firmware sleep parameter fields. `struct lbs_mesh_stats` collects mesh forwarding/drop counters under mesh config. `struct lbs_private` contains networking state, cfg80211 state, mesh/debugfs pointers, power/deep-sleep/host-sleep state, hardware callbacks, adapter identity, command queues and timers, response buffers, event FIFO, worker threads, encryption/WOL/TX state, locks, radio/channel/rate/power state, scanning state, and async firmware loading fields. `lbs_iface_active()` checks normal and mesh netdev running state.

Control flow and integration: almost every Libertas subsystem receives `lbs_private`. Bus drivers fill hardware callbacks and card pointer; main initializes locks, queues, threads, and netdevs; cfg/command/debugfs/ethtool mutate their slices of state.

State and persistence: all fields are in-memory runtime state. Firmware and EEPROM-derived values such as `fwrelease`, `fwcapinfo`, `regioncode`, and MAC address persist only while the device is loaded. Firmware settings are mirrored through commands.

Dependencies and risks: the struct depends on defs, decls, host command definitions, kfifo, cfg80211, netdev, timers, wait queues, and workqueues. Because it is large and shared, locking discipline matters: `lock`, `driver_lock`, serialized netdev xmit, wait queues, and timers protect different subsets. Test signals include probe/remove failure unwinds, suspend/resume, concurrent command/event/TX paths, scan cancellation, debugfs removal, and mesh-enabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/ethtool.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/ethtool.c

Purpose: this file implements Libertas ethtool operations for driver/firmware info, EEPROM reads, Wake-on-LAN configuration, and optional mesh statistics.

Important APIs: `lbs_ethtool_get_drvinfo()` formats firmware version and driver version. `lbs_ethtool_get_eeprom_len()` returns a fixed 16 KiB EEPROM size. `lbs_ethtool_get_eeprom()` bounds checks offset/length, sends `CMD_802_11_EEPROM_ACCESS`, and copies firmware-returned bytes. `lbs_ethtool_get_wol()` maps `priv->wol_criteria` to ethtool `WAKE_*` flags. `lbs_ethtool_set_wol()` validates flags and updates `wol_criteria`. `lbs_ethtool_ops` exports the table.

Control flow and state: ethtool userspace calls enter via netdev ops. EEPROM reads synchronously command firmware. WOL set only mutates `priv->wol_criteria`; host sleep/debugfs paths later apply criteria to firmware. Mesh stats callbacks are compiled in only under `CONFIG_LIBERTAS_MESH`.

Dependencies and integration: depends on netdevice ethtool, `cmd.c` command helper, mesh helpers, `lbs_driver_version`, firmware release formatting, and WOL constants from `defs.h`.

Risks and tests: EEPROM length is hard-coded for 8388-era parts; other hardware would need updates. WOL options are stored but not immediately sent. Test signals include `ethtool -i`, bounded `ethtool -e` reads including max length rejection, WOL get/set round trips, and mesh stats availability when configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/ethtool.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/firmware.c -->
## sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/firmware.c

Purpose: this file loads Libertas firmware by card model, supporting both async and legacy synchronous APIs and both one-stage helper-only and two-stage helper-plus-main firmware arrangements.

Important functions: `lbs_get_firmware_async()` records device, model, firmware table, callback, and starts table iteration. `load_next_firmware_from_table()` skips non-matching models, releases stale helper firmware, and requests the next helper. `helper_firmware_cb()` either requests the main firmware or reports helper-only success. `main_firmware_cb()` reports two-stage success. `lbs_fw_loaded()` calls the bus/core callback, clears `fw_callback`, and wakes `fw_waitq`. `lbs_wait_for_firmware_load()` waits for async completion. `lbs_get_firmware()` is the deprecated synchronous table-search equivalent.

Control flow: async loading uses `request_firmware_nowait()` for helper and optional main firmware. Missing firmware advances to the next table entry until a null helper terminator produces `-ENOENT`. Success passes firmware pointers to the caller callback; this file releases references after callback in the async path, so consumers must use them during callback or take their own references according to the surrounding driver contract.

State and persistence: `lbs_private` stores `fw_device`, `fw_table`, `fw_iter`, `fw_model`, `helper_fw`, and `fw_callback`. Firmware objects are kernel firmware references and not persisted by this file.

Dependencies and integration: bus drivers provide firmware tables and callbacks; core shutdown can wait for completion. The firmware loader subsystem and module reference handling are central dependencies.

Risks and tests: callback lifetime is subtle because async callbacks release firmware after notifying. Table iteration must avoid mismatched helper/main pairs and release helper on failure. Test signals include missing helper fallback, one-stage devices, two-stage devices, concurrent async call returning `-EBUSY`, wait completion, and synchronous fallback cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas/firmware.c -->
