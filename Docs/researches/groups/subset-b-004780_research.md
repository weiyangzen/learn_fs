# Research: subset-b-004780

Grouped research report for subset B work item `subset-b-004780`. Each section is source-tree aligned and wrapped for reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wmi.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wmi.c

## Purpose
`wmi.c` implements the host-side Wireless Module Interface for the Qualcomm Atheros/Wilocity `wil6210` 60 GHz wireless driver. It translates driver operations into firmware mailbox commands, receives firmware events from the mailbox, routes those events to cfg80211/netdev/ring-management handlers, and owns the firmware address-remapping tables used when host code dereferences firmware-provided buffers.

The file is central to device bring-up, connection management, scan reporting, AP/PCP operation, P2P discovery, block-ack negotiation, suspend/resume, EDMA ring setup, management frame Tx/Rx, link statistics, temperature reads, LED control, and firmware capability-gated features.

## Important APIs, Types, and Functions
- Module parameters:
  - `max_assoc_sta` caps AP station count against firmware and driver limits.
  - `agg_wsize` controls automatic Tx Block Ack establishment.
  - `led_id` selects the device LED for firmware LED configuration.
- Firmware memory maps:
  - `sparrow_fw_mapping`, `talyn_fw_mapping`, `talyn_mb_fw_mapping`, and `sparrow_d0_mac_rgf_ext` define linker-to-host address mappings.
  - `fw_mapping[MAX_FW_MAPPING_TABLE_SIZE]` is the active mapping table used by WMI buffer validation.
  - `wil_find_fw_mapping()` returns a mapping by section name.
  - `wmi_addr_remap()`, `wmi_buffer_block()`, `wmi_buffer()`, and `wmi_addr()` validate alignment, BAR bounds, overflow, and host-visible offsets before returning `__iomem` pointers.
- Mailbox command APIs:
  - `wmi_send()` serializes asynchronous firmware commands through `wil->wmi_mutex`.
  - `wmi_call()` sends a command and waits for a matching event ID/MID completion through `wil->wmi_call`.
  - `__wmi_send()` builds `wil6210_mbox_hdr` plus `wmi_cmd_hdr`, writes command payloads to the Tx mailbox ring, advances the hardware head, traces the command, and interrupts firmware with `SW_INT_MBOX`.
  - `wmi_read_hdr()` reads a mailbox header through validated firmware buffer addressing.
- Event receive and dispatch:
  - `wmi_recv_cmd()` runs from the threaded IRQ path, drains Rx mailbox descriptors, copies events into `pending_wmi_event`, completes immediate `wmi_call()` replies, and queues `wil->wmi_event_worker`.
  - `wmi_event_worker()`, `next_wmi_ev()`, and `wmi_event_handle()` run deferred event handling in workqueue context.
  - `wmi_evt_handlers[]` maps selected event IDs to handlers.
  - `wmi_event_flush()` drops queued events during reset/teardown.
  - `wil_is_wmi_idle()` checks pending event queue, active synchronous call, and mailbox Rx head/tail for power-management idleness.
- Key event handlers:
  - `wmi_evt_ready()` records firmware readiness, max VIF/MID support, firmware version, calibration status, max AP association count, recovery state, and completes `wil->wmi_ready`.
  - `wmi_evt_rx_mgmt()` and `wmi_evt_sched_scan_result()` validate variable event lengths, derive 60 GHz channel/frequency, and report BSS or management frames to cfg80211.
  - `wmi_evt_scan_complete()` completes cfg80211 scans and schedules delayed P2P listen if needed.
  - `wmi_evt_connect()` validates connect payload lengths/CID, initializes Tx rings, notifies station or AP cfg80211 paths, updates STA status, and tracks connected VIFs.
  - `wmi_evt_disconnect()` calls `wil6210_disconnect_complete()` and may notify packet loss in host-AP-SME mode.
  - `wmi_evt_eapol_rx()` reconstructs Ethernet EAPOL frames from firmware events and injects them into the network stack.
  - `wmi_evt_ring_en()`, `wmi_evt_ba_status()`, `wmi_evt_addba_rx_req()`, and `wmi_evt_delba()` coordinate data-port opening and AMPDU state.
  - `wmi_evt_auth_status()` and `wmi_evt_reassoc_status()` handle FT roaming auth/reassoc events, key removal, ring modify, and cfg80211 FT/roam notifications.
  - `wmi_evt_link_stats()` parses variable link-stat records and stores basic/global firmware stats.
  - `wmi_evt_link_monitor()` maps firmware RSSI threshold notifications to cfg80211 CQM events.
- Command helpers:
  - Basic firmware/device commands: `wmi_echo()`, `wmi_set_mac_address()`, `wmi_led_cfg()`, `wmi_rbufcap_cfg()`.
  - AP/PCP/P2P: `wmi_pcp_start()`, `wmi_pcp_stop()`, `wmi_set_ssid()`, `wmi_get_ssid()`, `wmi_set_channel()`, `wmi_get_channel()`, `wmi_p2p_cfg()`, `wmi_start_listen()`, `wmi_start_search()`, `wmi_stop_discovery()`, `wmi_port_allocate()`, `wmi_port_delete()`.
  - Security and IEs: `wmi_add_cipher_key()`, `wmi_del_cipher_key()`, `wmi_set_ie()`, `wmi_update_ft_ies()`.
  - Rx/Tx/rings: `wmi_rxon()`, `wmi_rx_chain_add()`, `wil_wmi_tx_sring_cfg()`, `wil_wmi_rx_sring_add()`, `wil_wmi_cfg_def_rx_offload()`, `wil_wmi_rx_desc_ring_add()`, `wil_wmi_tx_desc_ring_add()`, `wil_wmi_bcast_desc_ring_add()`.
  - Management frames and scans: `wmi_abort_scan()`, `wmi_start_sched_scan()`, `wmi_stop_sched_scan()`, `wmi_mgmt_tx()`, `wmi_mgmt_tx_ext()`.
  - Block Ack: `wmi_addba()`, `wmi_delba_tx()`, `wmi_delba_rx()`, `wmi_addba_rx_resp()`, `wmi_addba_rx_resp_edma()`.
  - Power and telemetry: `wmi_suspend()`, `wmi_resume()`, `wmi_ps_dev_profile_cfg()`, `wmi_get_temperature()`, `wmi_get_all_temperatures()`, `wmi_link_stats_cfg()`, `wmi_set_cqm_rssi_config()`, `wmi_set_mgmt_retry()`, `wmi_get_mgmt_retry()`.

## Control Flow
The outbound path begins with a driver subsystem constructing a WMI command payload from a `wmi.h` struct. `wmi_send()` or `wmi_call()` acquires `wil->wmi_mutex`, checks firmware readiness and suspend/resume restrictions, waits for a free Tx mailbox descriptor, copies the command header and payload into firmware-visible memory, marks the descriptor full, advances the mailbox head, traces the command, and raises a software interrupt to firmware. `wmi_call()` additionally installs `wil->reply_id`, `wil->reply_mid`, `wil->reply_buf`, and `wil->reply_size` under `wmi_ev_lock` and waits for `wil->wmi_call`.

The inbound path is intentionally split. `wmi_recv_cmd()` runs in the IRQ thread only long enough to copy firmware events out of the Rx mailbox, mark descriptors empty, advance the mailbox tail, and either complete a synchronous reply immediately or enqueue the event on `wil->pending_wmi_ev`. Deferred handlers then run in `wmi_event_worker()`, which avoids deadlocking the IRQ thread when event handling itself sends WMI commands.

Event dispatch validates the WMI mailbox type and header size, normalizes broadcast MID to MID 0, rejects events for invalid or absent VIFs, checks whether the event completes a pending `wmi_call()`, and otherwise dispatches through `wmi_evt_handlers[]`. Unknown WMI events are logged rather than fatal.

Higher-level flows sit on top of that transport. Connection events allocate/configure Tx rings before notifying cfg80211; disconnect events route to common disconnect completion; scan events feed cfg80211 BSS tables; scheduled scan result events report PNO results; EDMA setup commands synchronously wait for firmware tail pointers before enabling rings in driver state; suspend requires both the WMI suspend event and a later `suspend_resp_comp` wait condition.

## State and Persistence
Most state is in `struct wil6210_priv` and `struct wil6210_vif`, not persisted beyond driver runtime. Important mutable fields include `wil->status` bits, `wil->wmi_seq`, `wil->reply_*`, `wil->pending_wmi_ev`, mailbox ring head/tail shadows, `wil->sta[]`, Tx/Rx ring metadata, firmware capability bitmaps, suspend statistics, firmware stats caches, and per-VIF scan/connect state. Persistent storage is not used; firmware command state is reconstructed after reset and firmware readiness.

The active `fw_mapping[]` table is global driver state initialized elsewhere from the chip-specific constant maps in this file. LED blink timing and `led_polarity` are global runtime constants. Module parameters persist only as module configuration values.

## Dependencies and Integration Points
- Includes `wil6210.h`, `txrx.h`, `wmi.h`, and `trace.h`; depends on many driver-owned helpers and status bits.
- Uses Linux networking/cfg80211 APIs: `cfg80211_inform_bss_frame_data()`, `cfg80211_scan_done()`, `cfg80211_connect_bss()`, `cfg80211_connect_result()`, `cfg80211_new_sta()`, `cfg80211_del_sta()`, `cfg80211_rx_mgmt()`, `cfg80211_sched_scan_results()`, `cfg80211_ft_event()`, `cfg80211_roamed()`, `cfg80211_cqm_rssi_notify()`, and netdev stats delivery.
- Integrates with Tx/Rx code through `wil_ring_init_tx()`, `wil_addba_tx_request()`, `wil_addba_rx_request()`, `wil_tid_ampdu_rx_free()`, `wil->txrx_ops.tx_ring_modify()`, EDMA status/descriptor ring setup, and queue updates.
- Integrates with power management through `wil_is_wmi_idle()`, `wmi_suspend()`, `wmi_resume()`, HALP vote/unvote, suspend status bits, and `wil->wq`.
- Integrates with firmware recovery through `wil_set_recovery_state()`, `wil_fw_error_recovery()`, reset status checks, and mailbox-ready gating.
- Exposes public prototypes indirectly through `wil6210.h`; `wmi.h` supplies all command/event wire structs and IDs.

## Risks and Edge Cases
- Mailbox pointer validation is security- and stability-critical. Firmware-provided addresses must remain DWORD-aligned, remappable, inside BAR bounds, and non-overflowing; bugs here can turn malformed firmware events into invalid MMIO access.
- `__wmi_send()` assumes Tx mailbox descriptors become free within fixed retry loops. Firmware stalls surface as `-EBUSY` or timeouts and may cascade into recovery.
- `wmi_call()` supports one synchronous waiter per device through shared `wil->reply_*` state, so serialization by `wmi_mutex` is essential.
- Late events after a timed-out `wmi_call()` are explicitly dropped when they match a new pending reply with a reply buffer, reducing misdelivery but making timeout diagnosis important.
- Many firmware event payloads are variable length. The code has explicit checks for management, connect, FT, scheduled scan, and link-stat events, but any protocol drift in `wmi.h` can cause false rejection or under-validation.
- Several helpers truncate user/cfg80211 inputs to firmware maxima for scheduled scan match sets, channels, and plans; this is logged at debug level rather than treated as an error.
- Capability checks are uneven by feature: PNO and management retry are gated, AP SME partial offload is checked in `wmi_pcp_start()`, while many protocol structs are assumed compatible with the running firmware.
- Suspend/resume permits only traffic suspend/resume commands during suspend status bits. Incorrect status-bit transitions can block legitimate WMI activity.
- Connection event handling mutates STA and ring state before all cfg80211 notifications complete; error paths must reset `wil->sta[cid]` and connecting bits accurately.
- In `wmi_evt_auth_status()`, the FT roaming state check uses `wil->status` with `wil_vif_ft_roam`; this looks suspicious because the same bit is otherwise used with `vif->status`.

## Test Signals
- Build coverage should include `CONFIG_WIL6210`, normal DMA, enhanced DMA, AP, station, P2P, and suspend/resume code paths.
- Runtime smoke tests: firmware ready completion, `wmi_echo()`, MAC set, LED config when `led_id` is valid, SSID/channel set/get, temperature reads, and CQM RSSI config.
- cfg80211 integration tests: active scan completion, scheduled scan start/stop/result, station connect/disconnect, AP station add/remove, management frame Tx/Rx, FT auth/reassoc roaming, and EAPOL delivery.
- Ring tests: legacy Rx chain add, EDMA Tx/Rx status ring add, Rx descriptor ring add, Tx descriptor ring add, broadcast descriptor ring add, and returned hardware tail pointer sanity.
- Block Ack tests: ADDBA request/response, DELBA for Tx and Rx, extended CID/TID path, A-MSDU capability path, and `agg_wsize` values.
- Fault injection signals: WMI call timeout, mailbox ring full/head busy, invalid firmware buffer address, short/corrupt event lengths, invalid MID/CID/ring IDs, unsupported firmware capability, and suspend rejection paths.
- Tracepoints `trace_wil6210_wmi_cmd` and `trace_wil6210_wmi_event`, plus `wil_dbg_wmi` logs, are the main observability hooks for command/event sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wmi.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wmi.h

## Purpose
`wmi.h` is the generated protocol contract for the `wil6210` Wireless Module Interface. It defines all host-to-firmware command IDs, firmware-to-host event IDs, capability bits, fixed constants, command payload structures, event payload structures, packed wire formats, flexible-array payload conventions, status enums, and feature-specific configuration records used by the `wil6210` driver and firmware.

The header is not an implementation file; it is an ABI surface between host driver and firmware. Correct field layout, byte order, alignment, and enum values are essential for every WMI exchange in `wmi.c`, cfg80211 glue, Tx/Rx setup, debugfs, PMC, RF sector control, FTM/AOA, radar, power management, and link statistics.

## Important APIs, Types, and Data
- Top-level constants:
  - `WMI_MAC_LEN`, `WMI_MAX_SSID_LEN`, `WMI_MAX_IE_LEN`, `WMI_INVALID_TEMPERATURE`, `WMI_MAX_XIF_PORTS_NUM`, `WMI_QOS_*`, RF table lengths, scheduling limits, and firmware payload maxima.
  - `enum wmi_mid` defines default, debug, and broadcast MID addressing.
  - `enum wmi_fw_capability` maps firmware feature bits consumed by the driver.
- Common command header:
  - `struct wmi_cmd_hdr` contains MID, command/event ID, and firmware timestamp. It follows the mailbox header in every WMI message.
- Command namespace:
  - `enum wmi_command_id` assigns stable numeric IDs for connection, scan, security, management frame Tx, ring setup, BA control, RF/beamforming, power management, P2P, AP/PCP, FTM/AOA, RF sectors, EDMA ring setup, QoS, link stats, RBUFCAP, temperature, and vendor/internal commands.
- Event namespace:
  - `enum wmi_event_id` assigns stable numeric IDs for firmware ready, connect/disconnect, scan completion, management Rx/Tx, BA status, ring config completion, P2P/PCP/port events, suspend/resume, FTM/AOA, RF sectors, EDMA completion, link stats, CQM link monitor, command-not-supported, and internal firmware events.
- Core connection and scan structs:
  - `struct wmi_connect_cmd`, `struct wmi_disconnect_sta_cmd`, `struct wmi_connect_event`, `struct wmi_disconnect_event`.
  - `struct wmi_start_scan_cmd` with counted channel list, `struct wmi_start_sched_scan_cmd`, `struct wmi_sched_scan_result_event`, and PNO result structs.
  - `struct wmi_probed_ssid_cmd` and `struct wmi_set_appie_cmd`.
- Security structs:
  - `struct wmi_add_cipher_key_cmd`, `struct wmi_delete_cipher_key_cmd`, `enum wmi_key_usage`, and passphrase/key constants.
  - FT roaming structs `wmi_ft_auth_cmd`, `wmi_ft_reassoc_cmd`, `wmi_update_ft_ies_cmd`, `wmi_ft_auth_status_event`, and `wmi_ft_reassoc_status_event`.
- AP/P2P/port/power structs:
  - `struct wmi_bcon_ctrl_cmd`, `struct wmi_pcp_start_cmd`, `struct wmi_p2p_cfg_cmd`, `struct wmi_port_allocate_cmd`, `struct wmi_port_delete_cmd`.
  - `struct wmi_traffic_suspend_cmd`, `struct wmi_traffic_suspend_event`, `struct wmi_traffic_resume_event`, PS profile enums and structs.
- Ring and data-path structs:
  - Legacy ring structs `wmi_sw_ring_cfg`, `wmi_vring_cfg`, `wmi_vring_cfg_cmd`, `wmi_bcast_vring_cfg_cmd`, `wmi_cfg_rx_chain_cmd`.
  - EDMA structs `wmi_edma_ring_cfg`, `wmi_tx_status_ring_add_cmd`, `wmi_rx_status_ring_add_cmd`, `wmi_tx_desc_ring_add_cmd`, `wmi_rx_desc_ring_add_cmd`, `wmi_bcast_desc_ring_add_cmd`, and their completion events.
  - BA structs `wmi_ring_ba_en_cmd`, `wmi_ring_ba_dis_cmd`, `wmi_rcp_addba_resp_cmd`, `wmi_rcp_addba_resp_edma_cmd`, `wmi_rcp_delba_cmd`, `wmi_rcp_addba_req_event`, and `wmi_delba_event`.
- Management/telemetry structs:
  - `struct wmi_sw_tx_req_cmd`, `struct wmi_sw_tx_req_ext_cmd`, `struct wmi_rx_mgmt_info`, `struct wmi_rx_mgmt_packet_event`, and `struct wmi_tx_mgmt_packet_event`.
  - Temperature, LED, RSSI/link monitor, link stats, notify, RF status, firmware version, baseband type, and RBUFCAP structs.
- Advanced feature structs:
  - RF sector read/write/select/on commands and events.
  - FTM/TOF/AOA commands and events with variable destination/result arrays.
  - Radar configuration and PCI buffer control structs.
  - Rate search, beamforming, scheduling scheme, long range, QoS priority, internal firmware ioctl/event, and CCA indication structs.

## Control Flow
This header has no executable control flow. It describes the message formats used by executable control flow in `wmi.c` and other driver files. A typical flow is:

1. Driver code selects a `WMI_*_CMDID`, fills the matching packed command struct, converts multi-byte scalar fields to little endian, and sends it through `wmi_send()` or `wmi_call()`.
2. Firmware replies with a `WMI_*_EVENTID` and matching packed event struct.
3. `wmi.c` validates length, MID, status fields, and feature-specific payloads before mutating driver/cfg80211 state.

Flexible array members and counted arrays are common. Consumers must use `sizeof(base) + dynamic_len`, `offsetof(..., payload)`, `__struct_size()`, or `DEFINE_FLEX()` style helpers so that variable payloads are neither truncated nor overrun.

## State and Persistence
The header owns no runtime state. Its structs represent transient messages copied through mailbox buffers or DMA-visible firmware memory. Any lasting state is held by firmware or by driver structures populated from events, such as firmware capabilities, connection state, ring tail pointers, link statistics, RF sector data, and temperature readings.

The enum values and struct layouts are persistent ABI in the sense that firmware and host must agree across builds. The file comment identifies it as automatically generated, so manual changes are risky unless the generator and firmware contract are updated together.

## Dependencies and Integration Points
- Included by `wmi.c` and many `wil6210` subsystem files that build WMI payloads directly, including cfg80211, Tx/Rx, debugfs, PMC, main/netdev, interrupt, and PM code.
- Relies on Linux fixed-width and endian types such as `u8`, `s8`, `__le16`, `__le32`, and `__le64`.
- All command/event structs are `__packed`, making them wire-format definitions rather than normal in-memory kernel structs.
- Uses modern flexible-array annotations in several places, including `__counted_by`, `DECLARE_FLEX_ARRAY`, and open-ended arrays.
- Numeric IDs are used by `cmdid2name()` and `eventid2name()` in `wmi.c`, tracepoints, debugfs WMI injection, and firmware event dispatch.

## Risks and Edge Cases
- ABI drift is the largest risk. Reordering enum values, changing struct packing, changing field widths, or moving flexible arrays breaks firmware interoperability without necessarily causing compile errors.
- Multi-byte fields must be endian-converted at every use. The header marks fields as little-endian but cannot enforce conversions in callers.
- Several comments note deprecated commands/events. They remain in the ABI for compatibility and should not be reused casually.
- Some fields use sentinel values such as `MID_BROADCAST`, `CIDXTID_EXTENDED_CID_TID`, `WMI_INVALID_TEMPERATURE`, `WMI_LINK_MAINTAIN_CFG_CID_BROADCAST`, and `WMI_INVALID_RF_SECTOR_INDEX`; callers must preserve their special semantics.
- Compatibility values such as `WMI_NUM_MCS` remain for old fixed-size arrays while newer commands prefer dynamic arrays. Mixing old and new rate-search formats can cause sizing mistakes.
- Counted variable payloads must be bounded by firmware maxima such as `WMI_MAX_IOCTL_PAYLOAD_SIZE`, `WMI_MAX_INTERNAL_EVENT_PAYLOAD_SIZE`, `WMI_MAX_IE_LEN`, and feature-specific max counts.
- Some arrays and sizes are coupled by comments rather than code, for example RF DTYPE/ETYPE/RX2TX configuration lengths. Generated output must keep these synchronized.
- `wmi_delete_cipher_key_cmd` does not encode key usage even though `wmi_del_cipher_key()` accepts it; driver/firmware behavior depends on command semantics outside this struct.

## Test Signals
- Compile tests should catch missing struct names, enum names, and flexible-array annotations used by the rest of the driver.
- ABI-oriented tests should verify `sizeof()` and `offsetof()` for command/event structs that have firmware-visible layouts, especially mailbox header adjacency, EDMA ring commands, connect/scan events, and variable payload bases.
- Runtime tests should exercise representative command/event pairs: echo, ready, connect/disconnect, scan complete, management Tx/Rx, ring config done, BA request/response, suspend/resume, link monitor, link stats, and temperature.
- Fuzz or fault-injection tests should feed short, oversized, inconsistent, and unsupported event payloads to ensure `wmi.c` length checks match this header.
- Cross-version firmware tests are important whenever generated WMI definitions change, particularly around capability-gated features and command-not-supported handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/wmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/atmel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/atmel/Kconfig

## Purpose
This Kconfig file defines the Atmel wireless vendor menu and the selectable configuration symbol for the Atmel `at76c50x` USB 802.11 driver. It controls whether Atmel wireless options appear in kernel configuration and whether the `at76c50x-usb` driver can be built.

## Important APIs, Types, and Symbols
- `config WLAN_VENDOR_ATMEL`
  - Boolean vendor gate labeled "Atmel devices".
  - Defaults to `y`, which keeps Atmel wireless driver prompts visible by default.
  - Does not itself build code; it controls visibility of nested Atmel device options.
- `if WLAN_VENDOR_ATMEL` groups vendor-specific driver prompts.
- `config AT76C50X_USB`
  - Tristate option labeled "Atmel at76c503/at76c505/at76c505a USB cards".
  - Depends on `MAC80211 && USB`, ensuring the driver is only offered when mac80211 and USB support are available.
  - Selects `FW_LOADER`, because the device driver requires the kernel firmware loading facility.
  - Help text describes support for USB wireless devices using Atmel at76c503, at76c505, or at76c505a chips.

## Control Flow
Kconfig evaluation is declarative. When `WLAN_VENDOR_ATMEL=n`, the configurator skips the nested `AT76C50X_USB` prompt. When the vendor gate is enabled and dependencies are met, `AT76C50X_USB` may be set to `y`, `m`, or `n`. That value is consumed by the local Makefile through `obj-$(CONFIG_AT76C50X_USB)`.

## State and Persistence
The persistent state is the user's kernel configuration, typically `.config`. `WLAN_VENDOR_ATMEL` affects menu visibility; `AT76C50X_USB` affects build output. No runtime state is created by this file.

## Dependencies and Integration Points
- Integrated by the parent wireless driver Kconfig tree under `drivers/net/wireless`.
- `AT76C50X_USB` integrates with the local `Makefile`, which builds `at76c50x-usb.o` when the symbol is enabled.
- Depends on the mac80211 stack (`MAC80211`) and USB core (`USB`).
- Selects firmware loader support (`FW_LOADER`) for runtime firmware requests by the driver.

## Risks and Edge Cases
- `select FW_LOADER` forces firmware-loader availability but does not encode any specific firmware file names or packaging requirements.
- If `WLAN_VENDOR_ATMEL` is disabled, users may not see `AT76C50X_USB` even when hardware support is otherwise possible.
- The symbol is a tristate, so build and module-install tests need to cover both built-in and module modes.
- Because vendor gates are mostly UI controls, changing the default from `y` would alter discoverability more than driver semantics.

## Test Signals
- Kconfig tests or manual configuration should verify that `AT76C50X_USB` is hidden when `WLAN_VENDOR_ATMEL=n`.
- With `MAC80211=y/m` and `USB=y/m`, `AT76C50X_USB` should be selectable as built-in or module according to dependency tristate rules.
- Build tests should confirm that enabling `CONFIG_AT76C50X_USB=m` produces the expected `at76c50x-usb` module and that firmware-loader symbols are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/atmel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/atmel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/atmel/Makefile

## Purpose
This Makefile connects the Atmel wireless Kconfig symbol to the kernel build system. Its only build rule compiles and links the Atmel `at76c50x` USB wireless driver object when `CONFIG_AT76C50X_USB` is enabled.

## Important APIs, Types, and Targets
- SPDX license line: `GPL-2.0-only`.
- `obj-$(CONFIG_AT76C50X_USB) += at76c50x-usb.o`
  - If `CONFIG_AT76C50X_USB=y`, `at76c50x-usb.o` is built into the kernel image.
  - If `CONFIG_AT76C50X_USB=m`, it is built as a loadable module.
  - If the symbol is unset, no object is built from this directory entry.

## Control Flow
The kernel kbuild system expands `obj-y` and `obj-m` from the `obj-$(CONFIG_...)` assignment. There is no imperative flow in this file. Build behavior is entirely determined by the value selected through `drivers/net/wireless/atmel/Kconfig`.

## State and Persistence
The Makefile has no runtime state. Build state is represented by generated object files, modules, and dependency files in the kernel build output directory. Source state is a single declarative object mapping.

## Dependencies and Integration Points
- Consumes `CONFIG_AT76C50X_USB` defined in the adjacent Kconfig file.
- Integrates with the parent wireless Makefile through normal recursive kbuild directory traversal.
- The object name implies a companion source file `at76c50x-usb.c` in the same directory, built under mac80211/USB dependencies from Kconfig.

## Risks and Edge Cases
- If the object filename drifts from the actual source/module name, enabling `CONFIG_AT76C50X_USB` fails at build time.
- Dependency correctness lives in Kconfig, not this Makefile; adding objects here without updating Kconfig can expose build failures under incomplete configurations.
- Since there is only one object, any future split into multiple compilation units must preserve the module composition expected by kbuild.

## Test Signals
- `CONFIG_AT76C50X_USB=y` should include `at76c50x-usb.o` in built-in wireless objects.
- `CONFIG_AT76C50X_USB=m` should produce an `at76c50x-usb.ko` module.
- `CONFIG_AT76C50X_USB=n` should not build the object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/atmel/Makefile -->
