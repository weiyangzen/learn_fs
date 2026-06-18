# Research: subset-b-004965

Grouped source research for subset B work item `subset-b-004965`. Each delimited section preserves the source path and can be split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_mac80211.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_mac80211.c

## Purpose
This file is the RSI 91x mac80211/cfg80211 integration layer. It advertises supported channels, rates, interface combinations, AP station limits, WoWLAN, CQM, remain-on-channel, and antenna capabilities, then implements the `ieee80211_ops` callbacks that translate Linux wireless stack events into RSI firmware management commands.

## Important APIs, Types, and Functions
Important static data includes `rsi_2ghz_channels`, `rsi_5ghz_channels`, `rsi_rates`, `rsi_mcsrates`, `rsi_max_ap_stas`, `rsi_iface_limits`, `rsi_iface_combinations`, and `mac80211_ops`. Major entry points are `rsi_mac80211_attach`, `rsi_mac80211_detach`, `rsi_mac80211_tx`, `rsi_mac80211_start`, `rsi_mac80211_stop`, `rsi_mac80211_add_interface`, `rsi_mac80211_remove_interface`, `rsi_mac80211_config`, `rsi_mac80211_bss_info_changed`, `rsi_mac80211_set_key`, `rsi_mac80211_ampdu_action`, `rsi_mac80211_sta_add`, `rsi_mac80211_sta_remove`, `rsi_indicate_pkt_to_os`, `rsi_indicate_tx_status`, `rsi_config_wowlan`, and the ROC helpers.

## Control Flow
Attach allocates `ieee80211_hw`, binds `hw->priv` to `struct rsi_hw`, sets mac80211 feature flags, registers bands/rates, fills wiphy capabilities, installs the regulatory notifier, and registers the hardware. Runtime callbacks lock `common->mutex`, update shared RSI state, and call management helpers in `rsi_91x_mgmt.c` such as VAP capabilities, RX filter, channel, radio updates, key loading, BSS peer notification, aggregation parameters, background scan, WoWLAN, antenna, and block/unblock frames. RX data from bus code reaches `rsi_indicate_pkt_to_os`, which fills `ieee80211_rx_status`, strips IV/MIC fields for firmware-decrypted protected frames, runs CQM checks on connected beacons, and calls `ieee80211_rx_irqsafe`. TX status reverses internal headroom and reports ACK state with `ieee80211_tx_status_irqsafe`.

## State and Persistence Behavior
The file mutates `adapter->hw`, `adapter->sbands[]`, `adapter->vifs[]`, `adapter->sc_nvifs`, `common->vif_info[]`, `common->p2p_enabled`, `common->iface_down`, `common->hwscan`, `common->bgscan_en`, `common->hw_data_qs_blocked`, `common->secinfo`, `common->rate_config[]`, `common->bitrate_mask[]`, `common->stations[]`, `common->num_stations`, `common->key`, `common->cqm_info`, `common->uapsd_bitmap`, `common->wow_flags`, `common->beacon_interval`, `common->beacon_enabled`, `common->roc_timer`, `common->roc_vif`, `common->ant_in_use`, DFS region/country state, and power-save state through `adapter->ps_state`. Supported-band channel arrays are heap-copied and freed on detach; there is no durable on-disk persistence.

## Dependencies and Integration Points
It depends on mac80211/cfg80211, regulatory callbacks, SKB control blocks, RSI management APIs, RSI power-save helpers, debugfs setup/removal, SDIO header constants for shared queue values, and bus-level initialization that has already loaded firmware and populated `common->mac_addr`/band count. It is called from the management FSM when firmware MAC initialization completes.

## Risks
The callback surface is broad and stateful: missing mutex coverage can race VIF removal, RX delivery, station records, scans, or suspend/resume. `rsi_mac80211_add_interface` increments `sc_nvifs` before VAP programming returns, so a VAP setup failure can leave local state inconsistent. U-APSD bitmap operations use queue indices as bit masks, which is fragile. Key deletion zeroes the caller's `ieee80211_key_conf` before firmware loading. RX protected-frame header adjustment assumes firmware layout and can corrupt SKBs if descriptors or cipher state drift. ROC and scan timers need careful teardown during interface removal and suspend.

## Test Signals
Useful signals are mac80211 registration/unregistration, multi-VIF STA/AP/P2P combinations, channel changes while associated, AP station add/remove, WEP/TKIP/CCMP key install/delete, AMPDU start/stop, hardware background scan start/cancel/complete, CQM RSSI events, WoWLAN suspend/resume, remain-on-channel expiry/cancel, antenna set/get, rfkill polling, RX decrypt metadata, and debugfs cleanup during disconnect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_mac80211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_main.c

## Purpose
This file provides the bus-independent RSI 91x core object lifecycle, debug logging, RX packet demultiplexing, TX scheduler thread, and optional Bluetooth coexistence callbacks. SDIO and USB probes call `rsi_91x_init`, then transport code supplies host-interface operations and starts firmware initialization.

## Important APIs, Types, and Functions
Exports include `rsi_zone_enabled`, `rsi_dbg`, `rsi_read_pkt`, `rsi_91x_init`, and `rsi_91x_deinit`. Internal helpers include `opmode_str`, `rsi_print_version`, `rsi_prepare_skb`, and `rsi_tx_scheduler_thread`. With `CONFIG_RSI_COEX`, `g_proto_ops`, `rsi_get_host_intf`, `rsi_set_bt_context`, and `rsi_attach_bt` bridge the WLAN driver to the Bluetooth side.

## Control Flow
Initialization allocates `struct rsi_hw` and `struct rsi_common`, initializes all software TX queues, events, mutexes, the TX scheduler thread, default power-save and background-scan parameters, ROC timer, completions, operating mode, and coexistence mode. The TX scheduler waits on `common->tx_thread.event` with a bus-supplied timeout, then runs `rsi_core_qos_processor` once `init_done` is true. RX bytes from SDIO or USB enter `rsi_read_pkt`, which walks one or more frame descriptors, extracts queue number/length/extended descriptor, and dispatches packets to coexistence, WLAN management, WLAN data, or Bluetooth callbacks. Deinit stops the TX thread, purges queues, detaches BT/coex, clears `init_done`, and frees core objects and bus-private storage.

## State and Persistence Behavior
The file owns process-lifetime heap state for `adapter` and `common`, queue contents in `common->tx_queue[]`, `common->coex_mode`, `common->oper_mode`, `common->init_done`, `common->bt_defer_attach`, `common->bt_adapter`, and thread/event state. Debug zones are module-global and exported. No persistent state survives module unload; firmware and EEPROM state are handled elsewhere.

## Dependencies and Integration Points
It depends on `rsi_mgmt_pkt_recv`, `rsi_indicate_pkt_to_os`, `rsi_core_qos_processor`, `rsi_default_ps_params`, `init_bgscan_params`, optional `rsi_coex_*`, optional `rsi_bt_ops`, and bus callbacks `determine_event_timeout`. Transport drivers use this file as their common allocation and teardown layer.

## Risks
RX descriptor parsing trusts packet layout and casts unaligned descriptor bytes directly to `u16`, which is risky on strict-alignment architectures. `rsi_prepare_skb` truncates oversized USB packets but still relies on descriptor-provided offsets. TX thread shutdown assumes the thread was created and will complete. Coexistence attach may be deferred until MAC init; wrong FSM transitions can miss BT attach. Deinit frees `adapter->rsi_dev`, so transport disconnect paths must not use that pointer afterward.

## Test Signals
Probe/remove loops for USB and SDIO, RX demux for data/mgmt/coex/BT queues, invalid queue handling, multi-frame USB aggregates, TX scheduler wakeups under buffer-full timeouts, coexistence mode selection for all module `dev_oper_mode` values, deferred BT attach, and queue purge on unload are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_mgmt.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_mgmt.c

## Purpose
This file builds and processes RSI firmware management frames. It owns the WLAN firmware initialization FSM after card-ready, programs boot/radio/baseband parameters, converts mac80211 state changes into command SKBs, handles firmware confirmations, and forwards received 802.11 management frames into mac80211.

## Important APIs, Types, and Functions
Static boot tables `boot_params_20`, `boot_params_40`, `boot_params_9116_20`, and `boot_params_9116_40` carry PLL/clock setup. Key APIs include `init_bgscan_params`, `rsi_hal_send_sta_notify_frame`, `rsi_send_aggregation_params_frame`, `rsi_set_vap_capabilities`, `rsi_hal_load_key`, `rsi_band_check`, `rsi_set_channel`, `rsi_send_radio_params_update`, `rsi_send_vap_dynamic_update`, `rsi_inform_bss_status`, `rsi_send_block_unblock_frame`, `rsi_send_rx_filter_frame`, `rsi_send_ps_request`, `rsi_set_antenna`, `rsi_send_bgscan_params`, `rsi_send_bgscan_probe_req`, `rsi_handle_card_ready`, and `rsi_mgmt_pkt_recv`.

## Control Flow
All outbound commands are allocated as SKBs, filled with RSI descriptors, queued to `MGMT_SOFT_Q` or `MGMT_BEACON_Q`, marked internal when appropriate, and signaled to the TX scheduler. Card-ready handling begins in `FSM_CARD_NOT_READY`, sends common device parameters, then on WLAN HAL ready loads 9113 or 9116 boot parameters. Confirm handling advances through boot params, EEPROM MAC/RF reads for 9113 or MAC extraction for 9116, reset-MAC, radio capabilities, optional 9116 feature enable, BB/RF programming, and finally `FSM_MAC_INIT_DONE`, at which point it attaches mac80211 or completes a hibernate reinit. Normal runtime commands cover peer add/delete, key install, aggregation, VAP add/delete/update, channel and band changes, radio power updates, block/unblock, RX filtering, power save, antenna selection, beacon transmission, WoWLAN, and background scan.

## State and Persistence Behavior
This file initializes and mutates `common->fsm_state`, band/channel/channel-width/endpoint, `mac_addr`, `num_supp_bands`, EEPROM offset/length, `usb_buffer_status_reg`, RF reset and BB/RF programming counters, default EDCA/contention weights, power-save request fields, rate tables, `rate_config`, `hw_data_qs_blocked`, `mgmt_q_block`, `eapol4_confirm`, background-scan state, WoWLAN flags, `wlan_init_completion`, and beacon counters. Hardware-visible persistence consists of commands written into firmware RAM/register state; software state is volatile.

## Dependencies and Integration Points
It integrates with `rsi_91x_main.c` TX queues, host-interface bus write paths, firmware-loading HAL code, mac80211 attach/RX delivery, power-save confirm handling, channel/regulatory data, Bluetooth/coex queues, and many descriptor structures from `rsi_mgmt.h`/`rsi_hal.h`/`rsi_boot_params.h`.

## Risks
The FSM is order-sensitive; dropped or duplicate confirms can leave the device stuck or attach mac80211 before firmware is ready. Many frame builders assume fixed descriptor sizes and little-endian fields. `rsi_hal_load_key` copies WEP data as `key_len * 2` and unconditionally copies MIC material from offsets 16/24 when `data` is present, requiring cipher/key-length discipline. Background-scan code trusts `scan_req->n_channels` against firmware array capacity. `rsi_load_9116_bootup_params` clears only `sizeof(struct rsi_boot_params)` while allocating the larger 9116 frame. BSS status and queue blocking must align with privacy/EAPOL timing or data can be released early or remain blocked.

## Test Signals
Card-ready-to-MAC-init traces, 9113 EEPROM reads, 9116 boot feature path, firmware confirm fault injection, attach completion after hibernate reinit, command SKB descriptor validation, STA/AP association and disassociation, WEP/TKIP/CCMP key loading, fixed-rate and autorate tables, HT40 band switching, PS confirmations, beacon event handling, WoWLAN wake reasons, and background-scan completion are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_mgmt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_ps.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_ps.c

## Purpose
This file manages the host-side power-save state machine for RSI WLAN power save. It sets default sleep parameters, sends enable/disable requests through management code, reconfigures U-APSD while associated, and consumes firmware power-save confirmations.

## Important APIs, Types, and Functions
The public functions are `str_psstate`, `rsi_default_ps_params`, `rsi_enable_ps`, `rsi_disable_ps`, `rsi_conf_uapsd`, and `rsi_handle_ps_confirm`. The internal helper `rsi_modify_ps_state` logs and assigns `adapter->ps_state`.

## Control Flow
Defaults enable LP sleep with zero traffic thresholds, a default listen interval, and deep-sleep wake period. `rsi_enable_ps` accepts only `PS_NONE`, sends `rsi_send_ps_request(..., true, vif)`, and transitions to `PS_ENABLE_REQ_SENT`. `rsi_disable_ps` accepts only `PS_ENABLED`, sends a wakeup request, and transitions to `PS_DISABLE_REQ_SENT`. `rsi_conf_uapsd` temporarily disables and re-enables PS when U-APSD settings change. `rsi_handle_ps_confirm` reads the firmware confirm token and completes the pending transition to `PS_ENABLED` or `PS_NONE`.

## State and Persistence Behavior
The file mutates `adapter->ps_state` and initializes `adapter->ps_info`. State is volatile and represents a handshake with firmware, not durable configuration. The actual request payload is built in `rsi_91x_mgmt.c` from `ps_info`, association state, DTIM/listen values, and `common->uapsd_bitmap`.

## Dependencies and Integration Points
It is called from mac80211 config changes, association updates, WoWLAN setup, and firmware confirm handling. It depends on `rsi_send_ps_request`, `PS_CONFIRM_INDEX`, `RSI_SLEEP_REQUEST`, `RSI_WAKEUP_REQUEST`, `struct rsi_ps_info`, and `adapter->ps_lock` for callers that protect state transitions.

## Risks
The state machine rejects duplicate or out-of-order requests but only logs failures, so mac80211 PS state can diverge from firmware state. Confirm handling returns an error for unknown tokens but does not repair state. U-APSD reconfiguration assumes firmware accepts back-to-back disable/enable requests. Callers must hold the correct lock because this file does not lock internally.

## Test Signals
Exercise PS enable/disable from mac80211, firmware sleep/wakeup confirms, invalid confirms, repeated enable/disable requests, U-APSD toggles while associated, AP-mode PS suppression, WoWLAN coex PS disable, and suspend/resume transitions that reset `adapter->ps_state`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_ps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_sdio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_sdio.c

## Purpose
This file is the SDIO bus driver for RSI 9113/9116 WLAN devices. It probes SDIO IDs, creates the common RSI core, initializes SDIO function/block/FIFO state, supplies host-interface operations, starts the SDIO RX thread/IRQ path, loads firmware, handles reset/disconnect, and implements SDIO power-management hooks.

## Important APIs, Types, and Functions
Important helpers include `rsi_sdio_set_cmd52_arg`, `rsi_cmd52writebyte`, `rsi_cmd52readbyte`, `rsi_issue_sdiocommand`, `rsi_handle_interrupt`, `rsi_reset_card`, `rsi_setclock`, `rsi_setblocklength`, `rsi_setupcard`, `rsi_sdio_read_register`, `rsi_sdio_write_register`, `rsi_sdio_ack_intr`, `rsi_sdio_write_register_multiple`, `rsi_sdio_host_intf_read_pkt`, `rsi_sdio_reinit_device`, `rsi_sdio_ta_reset`, `rsi_probe`, `rsi_disconnect`, and PM callbacks. `sdio_host_intf_ops` connects this transport to the common HAL.

## Control Flow
Probe calls `rsi_91x_init`, sets `RSI_HOST_INTF_SDIO`, enables the SDIO function, sets block size/clock, initializes slave FIFO registers, determines the device model, starts `rsi_sdio_rx_thread`, claims the SDIO IRQ, then calls `rsi_hal_device_init` to load/boot firmware. Interrupts only wake the RX thread unless firmware is not loaded. Transmit packets go through `rsi_sdio_host_intf_write_pkt`, which maps the RSI queue into a block-count/address encoding and uses Cmd53 writes. Register and firmware-load paths use master-access MS-word selection and Cmd53 reads/writes. Disconnect stops RX, releases IRQ, detaches mac80211/BT, resets the chip/card, disables the function, and deinitializes common state.

## State and Persistence Behavior
The SDIO private object stores `pfunction`, block size, write-failure status, previous descriptor, interrupt/RX counters, buffer-full flags, packet buffer, and RX thread state. The common adapter records SDIO host ops, block size, event-timeout and queue-status callbacks, device model, hibernate/reinit flags, FSM state, and PM state. Hardware state is programmed through CCCR/FBR registers, FIFO controls, watchdog/reset registers, and SDIO master windows; all software state is per-probe.

## Dependencies and Integration Points
It depends on the Linux MMC/SDIO core, `rsi_91x_main.c` lifecycle, `rsi_hal_device_init`, SDIO operation helpers in `rsi_91x_sdio_ops.c`, mac80211 detach/rfkill, optional BT coex, and HAL register constants from `rsi_hal.h`.

## Risks
Manual SDIO card reinitialization in `rsi_reset_card` manipulates host `ios` directly and is sensitive to host-controller behavior. Error paths in interface init can leave `adapter->rsi_dev` allocated until common deinit. `write_fail` suppresses later writes and must be reset only when safe. Suspend sets `fsm_state` to card-not-ready while resume forces MAC-init without a full firmware replay; hibernate paths rely on `hibernate_resume` and later reinit. Register helpers skip host claiming when running in IRQ task context, so context tracking must be correct.

## Test Signals
Probe/remove for both 9113 and 9116 SDIO IDs, Cmd52/Cmd53 read/write failures, IRQ wake and RX packet processing, firmware load over SDIO, buffer-full backpressure, card reset and reload cycles, TA reset, suspend/resume/freeze/thaw/restore/shutdown with WoWLAN, coex attach/detach, and host-controller variants for high-speed/4-bit mode are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_sdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_sdio_ops.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_sdio_ops.c

## Purpose
This file contains SDIO-specific runtime operations for master register window setup, RX interrupt processing, slave-register initialization, hardware buffer-status tracking, and TX scheduler timeout selection.

## Important APIs, Types, and Functions
Public functions are `rsi_sdio_master_access_msword`, `rsi_sdio_rx_thread`, `rsi_init_sdio_slave_regs`, `rsi_sdio_check_buffer_status`, and `rsi_sdio_determine_event_timeout`. Internal helpers are `rsi_process_pkt` and `rsi_rx_handler`.

## Control Flow
`rsi_sdio_rx_thread` waits for the SDIO interrupt event and invokes `rsi_rx_handler` until shutdown. The handler reads `RSI_FN1_INT_REGISTER`, stores it in `adapter->interrupt_status`, handles buffer-available interrupts by refreshing queue status and waking the TX thread, handles firmware-assert interrupts by reading firmware status and marking the card not ready, handles packet-pending interrupts by reading the block count and packet buffer, and acknowledges unknown residual interrupts. Packet reads call `rsi_sdio_host_intf_read_pkt` followed by shared `rsi_read_pkt`. Slave-register init writes optional read delay, high-speed mode, read start level, and FIFO controls. Buffer-status checks update management/data full flags and return `QUEUE_FULL` or `QUEUE_NOT_FULL` to the common QoS scheduler.

## State and Persistence Behavior
This file mutates `adapter->interrupt_status`, `common->fsm_state`, `dev->rx_info` counters/flags, `dev->buff_status_updated`, and `dev->write_fail`. It also programs SDIO slave registers that persist in the device until reset. Timeout behavior becomes polling-like every 2 ms when the device reports data buffers full.

## Dependencies and Integration Points
It depends on register accessors and ACK helpers implemented in `rsi_91x_sdio.c`, common packet parsing in `rsi_read_pkt`, common TX scheduling through `common->tx_thread.event`, and queue IDs from RSI descriptors. Debugfs can expose some RX counters through the private SDIO state.

## Risks
The RX handler loops until it sees zero interrupt status; missed ACKs or a stuck interrupt can keep the RX thread active. Packet length is inferred from interrupt bits or `SDIO_RX_NUM_BLOCKS_REG`, so corrupt status can force invalid reads. Buffer-full state uses a static throttle counter shared across adapters. Firmware asserts only mark the FSM not ready; recovery depends on higher-level reset/disconnect. `rsi_sdio_rx_thread` increments `thread_done` on exit after the killer already increments it, which is harmless but unusual.

## Test Signals
Test interrupt cases for status zero, packet pending, buffer available, firmware assert, and unknown bits; RX block-count edge cases; queue-full transitions for management/data queues; TX scheduler wakeups when buffers clear; slave-register init errors; and sustained RX/TX under SDIO buffer pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_sdio_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_usb.c

## Purpose
This file is the USB bus driver for RSI 9113/9116 WLAN devices. It probes USB IDs, discovers bulk endpoints, initializes common RSI state, supplies USB host-interface operations, receives packets through URBs and an RX worker thread, performs vendor-control register access, loads firmware when needed, and resets/deinitializes hardware on disconnect.

## Important APIs, Types, and Functions
Important functions include `rsi_usb_card_write`, `rsi_write_multiple`, `rsi_find_bulk_in_and_out_endpoints`, `rsi_usb_reg_read`, `rsi_usb_reg_write`, `rsi_rx_done_handler`, `rsi_rx_urb_submit`, `rsi_usb_read_register_multiple`, `rsi_usb_write_register_multiple`, `rsi_usb_host_intf_write_pkt`, `rsi_usb_master_reg_read`, `rsi_usb_master_reg_write`, `rsi_usb_load_data_master_write`, `rsi_deinit_usb_interface`, `rsi_usb_init_rx`, `rsi_init_usb_interface`, `usb_ulp_read_write`, `rsi_reset_card`, `rsi_probe`, and `rsi_disconnect`. `usb_host_intf_ops` is the transport callback table.

## Control Flow
Probe creates the common adapter, initializes USB-private state, discovers WLAN and optional BT bulk endpoints, allocates a TX staging buffer, creates URBs and an RX thread, sets queue-status/timeout callbacks, determines device model, reads firmware status, loads firmware if not already running, and submits WLAN/BT RX URBs. RX URB completion validates length, queues the SKB to `dev->rx_q`, wakes `rsi_usb_rx_thread`, and resubmits the URB. TX packets route by RSI queue number to WLAN or BT endpoint and are written with bulk messages after adding USB headroom. Register and firmware loading use vendor control transfers in chunks. Disconnect detaches rfkill/mac80211/BT, kills URBs, resets the card through watchdog registers, frees RX/TX resources, and deinitializes common state.

## State and Persistence Behavior
USB-private state includes endpoint addresses/sizes, RX control blocks and URBs, RX queue, TX buffer, USB device pointer, write-failure flag, TX block size, and RX thread event/completion. The adapter records USB host ops, `RSI_HOST_INTF_USB`, block size, and debugfs entry count. Device state changes through vendor register writes, firmware image writes, TA hold/reset registers, and watchdog timers. USB PM callbacks currently return `-ENOSYS`.

## Dependencies and Integration Points
It depends on Linux USB core, `rsi_91x_main.c`, `rsi_91x_usb_ops.c` RX thread and queue-status helpers, common HAL firmware loading, optional BT coex, mac80211 detach/rfkill, and reset constants from `rsi_hal.h`.

## Risks
URB resubmission happens from completion context and must not leak or double-free SKBs on error. `rsi_usb_reg_read` writes `*value` before checking transfer status, so failed reads can expose stale control-buffer data. `rsi_usb_load_data_master_write` uses a fixed 256-byte stack buffer and assumes `block_size <= 256`. USB suspend/resume is unimplemented. Endpoint discovery assumes endpoint ordering maps WLAN first and BT second. Bulk writes serialize through a single TX buffer, so callers must preserve bus-level locking.

## Test Signals
Probe/remove for both USB product IDs, endpoint layouts with/without coex, firmware-already-loaded and firmware-load paths, URB completion/resubmit errors, RX queue overflow, WLAN/BT endpoint routing, vendor register read/write chunking, disconnect during active RX/TX, watchdog reset success/failure, and PM callback behavior should be exercised.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_usb_ops.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_usb_ops.c

## Purpose
This file provides the USB RX worker thread that drains SKBs queued by USB URB completion and feeds them into the shared RSI packet parser.

## Important APIs, Types, and Functions
The only function is `rsi_usb_rx_thread(struct rsi_common *common)`.

## Control Flow
The thread waits forever on `dev->rx_thread.event`, resets the event, and drains `dev->rx_q` until empty or shutdown. Each SKB is passed to `rsi_read_pkt(common, skb->data, 0)`, where zero length indicates USB framing rather than a pre-known aggregate byte count. On parser failure it logs and stops the inner drain loop; on shutdown it purges the RX queue and completes the thread completion.

## State and Persistence Behavior
It consumes and purges `struct rsi_91x_usbdev::rx_q`, observes `rx_thread.thread_done`, and completes `rx_thread.completion`. It does not persist hardware state. SKBs remain queued only until the thread drains them or the device is deinitialized.

## Dependencies and Integration Points
It depends on USB private state from `rsi_usb.h`, event helpers in `rsi_common.h`, and the common demultiplexer `rsi_read_pkt`. It is created in `rsi_usb_init_rx` and stopped from USB deinit.

## Risks
If `rsi_read_pkt` returns an error, the current implementation breaks before freeing that SKB, which can leak the failed packet. The thread assumes URB completion only enqueues valid SKBs and that `rsi_kill_thread` wakes the event before waiting. Since USB passes `rcv_pkt_len == 0`, descriptor offset validation in `rsi_read_pkt` is the primary guard against malformed packets.

## Test Signals
Queue drain under sustained URB completions, parser failure handling, thread shutdown with queued packets, RX queue purge on disconnect, and invalid USB aggregate descriptors are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_usb_ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_boot_params.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_boot_params.h

## Purpose
This header defines the packed boot-parameter structures and PLL/clock constants sent from the host to RSI firmware during early WLAN bring-up for 9113-style and 9116-style devices.

## Important APIs, Types, and Functions
Important macros include `VALID_20`, `VALID_40`, `UMAC_CLK_20BW`, `UMAC_CLK_40BW`, PLL M/N/P values, switch-clock bit flags, `LOADED_TOKEN`, `ROM_TOKEN`, `BT_COEXIST`, and `BOOTUP_MODE`. Data types include `tapll_info`, `pll960_info`, `afepll_info`, `pll_config`, `pll_config_9116`, `switch_clk`, `switch_clk_9116`, `device_clk_info`, `device_clk_info_9116`, `bootup_params`, and `bootup_params_9116`.

## Control Flow
There is no executable control flow. `rsi_91x_mgmt.c` instantiates concrete 20 MHz and 40 MHz boot tables from these layouts and copies them into management command SKBs after card-ready and when channel width changes.

## State and Persistence Behavior
The header stores no runtime state, but its packed little-endian structures become hardware-visible configuration for PLLs, clocks, wakeup waits, watchdog values, DCDC mode, sleep clock source, and boot mode. Incorrect field ordering or packing would persist into firmware until reset.

## Dependencies and Integration Points
It depends on Linux endian types and `BIT()`. It is tightly coupled to firmware management frame definitions in `rsi_mgmt.h` and to the init FSM in `rsi_91x_mgmt.c`.

## Risks
These layouts are firmware ABI. Changing field order, size, packing, endian conversion, or valid-bit masks can prevent boot, break RF clocks, or misprogram power/reset behavior. Macros such as `CUR_DEV_MODE_9116` reference an object name and are unsafe outside the expected initializer context.

## Test Signals
Build-time structure size/packing checks, firmware boot on 20/40 MHz modes, 9113 and 9116 card-ready transitions, channel-width changes that reload boot params, and hardware logs for PLL/clock programming are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_boot_params.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_coex.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_coex.h

## Purpose
This header declares the optional WLAN/Bluetooth coexistence control block and APIs used when `CONFIG_RSI_COEX` is enabled.

## Important APIs, Types, and Functions
It defines `COMMON_CARD_READY_IND`, `NUM_COEX_TX_QUEUES`, `struct rsi_coex_ctrl_block`, and prototypes for `rsi_coex_attach`, `rsi_coex_detach`, `rsi_coex_send_pkt`, and `rsi_coex_recv_pkt`.

## Control Flow
The header has no executable flow. In the implementation users, core initialization attaches coexistence for operating modes with BT, RX demux routes coex queue traffic to `rsi_coex_recv_pkt`, and the Bluetooth stack can transmit through `rsi_coex_send_pkt` via `rsi_proto_ops`.

## State and Persistence Behavior
`struct rsi_coex_ctrl_block` holds a back-pointer to `rsi_common`, coexistence TX queues, and a coexistence TX thread. State exists only while the module is loaded and coex is attached.

## Dependencies and Integration Points
It includes `rsi_common.h` and depends on SKB queues and the shared `rsi_thread` abstraction. Integration points are `rsi_91x_main.c`, RX queue demux, BT attach/detach callbacks, and bus packet transmission.

## Risks
Because all declarations are behind `CONFIG_RSI_COEX`, callers must guard references correctly. Queue numbering must stay consistent with firmware queue IDs. Coex teardown must stop its thread and purge SKBs before the shared `rsi_common` is freed.

## Test Signals
Builds with and without `CONFIG_RSI_COEX`, STA+BT/AP+BT operating modes, BT card-ready deferral, coex queue TX/RX ordering, and detach during active BT traffic are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_coex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_common.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_common.h

## Purpose
This header provides shared utility wrappers and cross-module declarations for the RSI common core, especially event/thread helpers used by TX, SDIO RX, USB RX, and coexistence worker threads.

## Important APIs, Types, and Functions
It defines `EVENT_WAIT_FOREVER`, `FIRMWARE_RSI9113`, `QUEUE_NOT_FULL`, `QUEUE_FULL`, inline helpers `rsi_init_event`, `rsi_wait_event`, `rsi_set_event`, `rsi_reset_event`, `rsi_create_kthread`, and `rsi_kill_thread`, plus prototypes for common/mac80211 lifecycle and packet APIs such as `rsi_mac80211_detach`, `rsi_mac80211_rfkill_exit`, `rsi_get_connected_channel`, `rsi_91x_init`, `rsi_91x_deinit`, `rsi_read_pkt`, `rsi_config_wowlan`, `rsi_find_sta`, `rsi_get_vif`, and `rsi_roc_timeout`.

## Control Flow
Event helpers implement an inverted condition convention: initialized/reset events have condition `1`, set events change it to `0` and wake waiters, and waiters block until it becomes `0`. Thread creation wraps `kthread_run`; thread killing sets `thread_done`, wakes the event, and waits for the thread's completion.

## State and Persistence Behavior
The inline helpers mutate `struct rsi_event` atomics/wait queues and `struct rsi_thread` task/completion state. No persistent storage is involved.

## Dependencies and Integration Points
It depends on `linux/kthread.h` and types from `rsi_main.h`/mac80211 declarations in compilation units. It is included by core, SDIO, USB, management, power-save, and coexistence code.

## Risks
The event convention is easy to misuse because "set" means condition zero. `rsi_kill_thread` assumes the thread was successfully created and will always complete. `rsi_create_kthread` casts `PTR_ERR` to `int`, which is normal but loses type annotation. Prototypes must match implementations gated by `CONFIG_PM` and optional modules.

## Test Signals
Thread start/stop for TX/RX/coex workers, wake-before-wait cases, repeated event resets, module unload under idle and active traffic, and builds with PM/coex/debugfs combinations validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_debugfs.h

## Purpose
This header abstracts optional RSI debugfs support. It provides no-op inline functions when debugfs support is disabled and declares debugfs file/container types and setup/removal functions when enabled.

## Important APIs, Types, and Functions
For non-debugfs builds, `rsi_init_dbgfs` returns success and `rsi_remove_dbgfs` does nothing. For debugfs builds, it defines `struct rsi_dbg_files`, `struct rsi_debugfs`, and declares `rsi_init_dbgfs` and `rsi_remove_dbgfs`.

## Control Flow
There is no executable flow in the enabled case. In disabled builds, inline stubs allow callers in mac80211 attach/detach to compile without conditionals around every invocation.

## State and Persistence Behavior
Enabled builds store debugfs dentries in `adapter->dfsentry` and `rsi_debugfs::rsi_files[]`. Debugfs files are runtime observability state only and must be removed on detach; there is no durable persistence.

## Dependencies and Integration Points
It includes `rsi_main.h` and `linux/debugfs.h`. `rsi_mac80211_attach` calls setup after successful hardware registration, and `rsi_mac80211_detach` removes files and frees the debugfs container.

## Risks
The debugfs entry count is transport-specific (`MAX_DEBUGFS_ENTRIES` for SDIO and one less for USB), so setup must honor `adapter->num_debugfs_entries`. Removal must tolerate partially created entries and detach after failed attach. Stub behavior can hide missing observability in non-debugfs builds.

## Test Signals
Builds with and without `CONFIG_RSI_DEBUGFS`, attach failure cleanup after partial debugfs creation, repeated probe/remove, and reading each debugfs file during traffic are relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_hal.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_hal.h

## Purpose
This header defines the host/firmware HAL constants, bootloader command values, firmware-load addresses, watchdog/reset registers, descriptor layouts, and HAL API prototypes shared by USB, SDIO, management, and core code.

## Important APIs, Types, and Functions
Important macro groups include `DEV_OPMODE_*` and `DEV_OPMODE_PARAM_DESC`, flash geometry, ping/pong firmware-load buffers, bootloader command/status bytes, ULP and 9116 watchdog registers, RF SPI/GSPI registers, firmware image limits, version offsets, register sizes, firmware alignment, and RAM access masks. Important types are `bl_header`, `ta_metadata`, `bootload_entry`, `bootload_ds`, `rsi_mgmt_desc`, `rsi_data_desc`, and `rsi_bt_desc`. Declared APIs include `rsi_hal_device_init`, `rsi_prepare_mgmt_desc`, `rsi_prepare_data_desc`, `rsi_prepare_beacon`, `rsi_send_pkt_to_bus`, and `rsi_send_bt_pkt`.

## Control Flow
The header has no executable flow. Its constants drive firmware loading, bootloader handshakes, descriptor preparation, queue selection, watchdog reset, register access, and packet transmission in the corresponding `.c` files.

## State and Persistence Behavior
No software state is stored here. The packed descriptor structures become on-bus ABI sent to firmware. Register constants target persistent device state until reset, especially firmware load buffers, bootloader control registers, watchdog timers, RF SPI controls, and memory-access permissions.

## Dependencies and Integration Points
It is included by USB/SDIO bus drivers, management frame builders, the common core, and HAL implementation files. It integrates with firmware file `rs9113_wlan_qspi.rps`, module operating mode parameters, and bus-specific `rsi_host_intf_ops`.

## Risks
This is a hardware/firmware ABI surface. Wrong constants or descriptor packing can break boot, corrupt packet descriptors, or reset the wrong block. `MAX_FLASH_FILE_SIZE` and alignment constants must match firmware images. Register-size mismatches between 9113 and 9116 paths can cause partial writes. Duplicate names such as common HAL card-ready constants must stay synchronized with management/coex definitions.

## Test Signals
Firmware load over SDIO and USB, bootloader ping/pong handshakes, flash size/version reads, descriptor decode by firmware for mgmt/data/BT packets, watchdog reset for 9113 and 9116, and builds across all transport/coex combinations validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_hal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_main.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_main.h

## Purpose
This is the central shared state and constant header for the RSI 91x WLAN driver. It defines debug zones, firmware FSM states, queue constants, data/control structures, common adapter state, hardware wrapper state, and host-interface operation callbacks.

## Important APIs, Types, and Functions
Important definitions include `enum RSI_FSM_STATES`, queue and watermark constants, WoWLAN flags, `enum rsi_dev_model`, `struct version_info`, `struct skb_info`, `enum edca_queue`, `struct security_info`, `struct wmm_qinfo`, `struct transmit_q_stats`, `struct rsi_bgscan_params`, `struct vif_priv`, `struct rsi_event`, `struct rsi_thread`, `struct cqm_info`, `enum rsi_dfs_regions`, `struct rsi_9116_features`, `struct rsi_rate_config`, `struct rsi_common`, `struct eepromrw_info`, `struct eeprom_read`, `struct rsi_hw`, and `struct rsi_host_intf_ops`.

## Control Flow
The header has no executable flow, but it defines the control surfaces used by the driver. `struct rsi_common` carries the firmware FSM, TX queues, locking, VIF/station tables, scans, PS, WoWLAN, AP, P2P, rate, security, and coexistence state. `struct rsi_hw` wraps mac80211 hardware, transport identity, power-save state, debugfs, firmware metadata, EEPROM, interrupt state, bus-private pointer, and function pointers used by bus-independent HAL code.

## State and Persistence Behavior
All major runtime state is shaped here: initialization and MAC FSM state, queue backlogs, locks, completion objects, channel/band, bitrate masks, security ciphers, EDCA parameters, firmware version, MAC address, RF/channel state, sleep configuration, beacon/AP station records, remain-on-channel timer, BT/coex references, background scan configuration, 9116 feature bits, EEPROM work buffers, and host-interface callbacks. State is in-memory per adapter and is rebuilt on probe or hibernate reinit.

## Dependencies and Integration Points
It includes Linux SKB/string headers, mac80211, public RSI 91x net header, and `rsi_ps.h`. It is the common include for core, mac80211, management, USB, SDIO, debugfs, coex, and power-save code.

## Risks
This header is a high-blast-radius contract: changing struct layout, queue constants, or FSM values affects nearly every file. Locking responsibilities are implicit in fields rather than encoded in helper APIs. `RSI_MAX_VIFS`, `RSI_MAX_ASSOC_STAS`, queue counts, and `MAX_HW_QUEUES` must stay aligned with firmware and mac80211 registration. Function pointer callbacks may be NULL for unsupported transports, so callers must check where optional.

## Test Signals
Full driver builds for USB/SDIO, PM, debugfs, and coex variants; probe/init/deinit; all FSM transitions; VIF/station/queue limits; rate mask and EDCA behavior; WoWLAN/PS/scanning/AP/P2P workflows; and static analysis for structure initialization coverage are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_main.h -->
