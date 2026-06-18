# Research: subset-b-004771

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_init.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_init.c

## Purpose

`htc_drv_init.c` is the probe, initialization, and teardown lane for the ath9k HTC USB driver. It binds an `htc_target` supplied by the USB HIF layer to a mac80211 `ieee80211_hw`, creates the WMI control channel, connects all HTC service endpoints, adapts shared ath9k register access to firmware-mediated WMI commands, initializes the common ath9k hardware core, registers the device with mac80211, and unwinds all of that on disconnect or initialization failure.

## Important APIs, Types, and Functions

The externally visible lifecycle functions are `ath9k_htc_probe_device()`, `ath9k_htc_disconnect_device()`, `ath9k_htc_suspend()`, `ath9k_htc_resume()`, and the module `ath9k_htc_init()`/`ath9k_htc_exit()` pair. `ath9k_htc_probe_device()` allocates `ieee80211_hw`, waits for target readiness, initializes WMI, connects services, initializes hardware and mac80211 state, then stores `htc_handle->drv_priv`. `ath9k_htc_disconnect_device()` sets `AH_UNPLUGGED` on hot unplug, unregisters/deinitializes mac80211 and hardware state, stops WMI, deallocates USB URBs, destroys WMI, and frees `ieee80211_hw`.

The service setup path is `ath9k_init_htc_services()`, with `ath9k_htc_connect_svc()` as a small helper for beacon, CAB, UAPSD, management, and four data AC services. WMI control uses `ath9k_wmi_connect()`. Endpoint IDs are saved in `priv->wmi_cmd_ep`, `beacon_ep`, `cab_ep`, `uapsd_ep`, `mgmt_ep`, and `data_*_ep`.

The register access adapter is a key API boundary. `ath9k_regread()`, `ath9k_multi_regread()`, `ath9k_regwrite()`, `ath9k_regwrite_multi()`, `ath9k_reg_rmw()`, and their buffer/flush helpers implement `struct ath_ops` over WMI commands such as `WMI_REG_READ_CMDID`, `WMI_REG_WRITE_CMDID`, and `WMI_REG_RMW_CMDID`. `ath_usb_eeprom_read()` reads EEPROM through remote registers, and `ath9k_usb_bus_ops` exposes USB bus callbacks to the shared hardware layer.

`ath9k_init_priv()` allocates and wires `struct ath_hw`, assigns register ops, bus ops, power-save ops, tasklets, delayed work, timers, locks, cache-line sizing, `ath9k_hw_init()`, queue setup, common channels/rates/crypto, miscellaneous defaults, and BT coexistence init. `ath9k_set_hw_capab()` translates hardware capabilities into mac80211/wiphy flags, interface combinations, bands, antenna masks, headroom, and extended features. `ath9k_init_device()` layers firmware version validation, regulatory init, TX/RX init, `ieee80211_register_hw()`, debugfs, LEDs, rfkill polling, and hardware name reporting.

## Control Flow

The normal probe sequence is: allocate mac80211 hardware, populate `priv`, wait for firmware `target_wait`, create WMI, connect WMI and HTC data services, set HTC credits according to USB device family, run `htc_init()`, initialize `ath_hw`, validate firmware version, register regulatory and mac80211 state, initialize TX/RX queues, then publish `priv->initialized` after a memory barrier so WMI event processing can safely proceed.

Error paths are layered in reverse order. Failures after WMI setup stop/destroy WMI and deallocate USB URBs. Failures after hardware init call `ath9k_deinit_priv()`. Failures after mac80211 registration unregister hardware before cleaning RX/TX. This file deliberately avoids setting the global `htc_handle->drv_priv` until initialization succeeds.

Suspend only asks the hardware core to enter `ATH9K_PM_FULL_SLEEP`. Resume waits for target readiness again, reconnects HTC services with the stored device IDs, and reconfigures LEDs.

## State and Persistence Behavior

Persistent driver state is mostly in `struct ath9k_htc_priv`, `struct htc_target`, and `struct ath_hw`. This file initializes `priv->ah`, `priv->wmi`, endpoint IDs, firmware version fields, `fw_flags`, `initialized`, WMI register batching counters, queue maps, locks, work items, tasklets, timers, beacon slots, spectral defaults, and `common` fields such as `macaddr`, `bssidmask`, `debug_mask`, `btcoex_enabled`, and `op_flags`.

The register write and RMW batching paths are stateful: `mwrite_cnt` and `m_rmw_cnt` gate whether writes are buffered; `multi_write_idx` and `multi_rmw_idx` are protected by mutexes and flushed on explicit flush or full buffer. Firmware versions older than 1.4 set `HTC_FWFLAG_NO_RMW`, causing `ath9k_reg_rmw()` to fall back to read-modify-write on the host.

## Dependencies and Integration Points

This file depends on `htc.h` for the HTC/WMI/private driver contract, the USB HIF layer for `ath9k_hif_usb_init()`, URB cleanup, and target readiness, mac80211/cfg80211 for device allocation and registration, the shared ath9k hardware core for `ath9k_hw_init()` and capability handling, common ath helpers for regulatory/crypto/rates, and optional debugfs/LED/rfkill/PM features.

## Risks

Remote register access is latency-sensitive and can fail independently of the host call site; most failures are logged but not always propagated once initialization is past the command boundary. The multi-register read helper uses fixed arrays of 8 elements, so callers must respect that implicit limit. Initialization ordering is tight: WMI tasklets are only safe after `priv->initialized`, and RX endpoint processing is separately gated by RX initialization. Cleanup must remain paired with the exact stage reached, especially on USB hot-unplug where `AH_UNPLUGGED` suppresses some warnings in lower layers. Firmware version and RMW capability mismatches can change register semantics across the whole hardware core.

## Test Signals

Useful test signals include successful module load/unload, USB probe and hot-unplug while traffic is active, firmware-ready timeout behavior, firmware version rejection, WMI service endpoint assignment logs, register read/write failure logs, `ieee80211_register_hw()` success, interface creation after probe, suspend/resume service reconnection, and no leaked URBs/SKBs across failed initialization stages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_main.c

## Purpose

`htc_drv_main.c` implements the mac80211 operation surface for ath9k HTC devices. It translates mac80211 start/stop, channel, interface, station, power-save, key, filter, scan, TSF, AMPDU, and rate-control requests into shared ath9k hardware operations plus WMI commands to the USB firmware target.

## Important APIs, Types, and Functions

The exported operation table is `struct ieee80211_ops ath9k_htc_ops`. Its callbacks include `ath9k_htc_tx()`, `ath9k_htc_start()`, `ath9k_htc_stop()`, `ath9k_htc_add_interface()`, `ath9k_htc_remove_interface()`, `ath9k_htc_config()`, `ath9k_htc_configure_filter()`, `ath9k_htc_sta_add()`, `ath9k_htc_sta_remove()`, `ath9k_htc_conf_tx()`, `ath9k_htc_set_key()`, TSF accessors, AMPDU handling, scan hooks, coverage class, bitrate mask, stats, antenna reporting, and channel-switch beacon tracking.

Power management centers on `ath9k_htc_setpower()`, `ath9k_htc_ps_wakeup()`, `ath9k_htc_ps_restore()`, and `ath9k_ps_work()`. These protect `ath9k_hw_setpower()` with `htc_pm_lock` and reference-count awake requests through `ps_usecount`.

Reset and channel transitions are handled by `ath9k_htc_reset()` and `ath9k_htc_set_channel()`. Both stop ANI, stop queues, delete the TX cleanup timer, drain host and target TX, disable firmware interrupts, stop receiving, drain WMI events, reset the hardware core, restart receive, set firmware PHY mode, re-enable interrupts, restart HTC, reconfigure VIF beacon/ANI state, wake queues, and restore power-save state.

Interface and station management uses WMI target objects: `ath9k_htc_add_interface()`/`remove_interface()` create/remove VAPs, `ath9k_htc_add_station()`/`remove_station()` create/remove target station entries, and special monitor helpers create an exclusive monitor VIF plus a station entry for injection. Rate information is marshalled through `ath9k_htc_setup_rate()`, `ath9k_htc_send_rate_cmd()`, `ath9k_htc_init_rate()`, and `ath9k_htc_update_rate()`. AMPDU state is coordinated by `ath9k_htc_tx_aggr_oper()`.

## Control Flow

`ath9k_htc_start()` wakes the chip, flushes receive state, maps mac80211's configured channel to an `ath9k_channel`, resets hardware, sets target mode via WMI, initializes firmware receive, updates target capabilities, clears `ATH_OP_INVALID`, starts HTC/HIF traffic, wakes mac80211 queues, arms the TX cleanup timer, and starts BT coexistence.

`ath9k_htc_stop()` performs the reverse while carefully leaving the main mutex before cancelling work that could need driver locks. It wakes power, disables interrupts, drains target TX, stops receive, kills RX tasklet, drains TX/WMI state, cancels work, stops ANI and BT coexistence, removes monitor mode if present, disables PHY and hardware, enters full sleep, and marks `ATH_OP_INVALID`.

Interface creation chooses a firmware opmode for station, IBSS, AP, or mesh; allocates VIF and station slots through bitmaps; sends `WMI_VAP_CREATE_CMDID` and `WMI_NODE_CREATE_CMDID`; updates BSSID masks; updates opmode; assigns beacon slots for beaconing modes; and starts ANI for AP operation. Removal sends `WMI_VAP_REMOVE_CMDID`, removes the VIF station, frees slots, updates opmode/BSSID mask, and stops ANI if no active users remain.

`ath9k_htc_config()` reacts to mac80211 change bits. Idle exit forces a reset, monitor changes add/remove a firmware monitor VIF, channel changes call `ath9k_htc_set_channel()`, PS changes enter/leave network sleep, and power changes update the hardware TX power limit.

## State and Persistence Behavior

The file maintains `priv->ps_usecount`, `ps_idle`, `ps_enabled`, `nvifs`, `nstations`, `vif_slot`, `sta_slot`, per-type VIF counters, `vif_sta_pos`, `mon_vif_idx`, `num_sta_assoc_vif`, `cur_beacon_conf`, `rearm_ani`, `reconfig_beacon`, `csa_vif`, `rxfilter`, and `curtxpow`. Station private state stores firmware station indices, rate update work, and TID aggregation state. Common hardware state includes `curbssid`, `curaid`, `op_flags`, TSF adjustment, slottime, and opmode.

## Dependencies and Integration Points

This file is the main integration point with mac80211 and cfg80211. It also calls WMI command helpers, HTC start/stop/drain APIs, ath9k common helpers for channels, TX power, RX filters, keys, and RSSI, beacon code, BT coexistence code, debug/stat helpers, and the shared hardware core in `hw.c`.

## Risks

Lock ordering is a primary risk: the file mixes `priv->mutex`, `htc_pm_lock`, `beacon_lock`, TX locks, RCU, work cancellation, tasklets, timers, and mac80211 callbacks. Power-save reference imbalance can leave the chip awake or asleep at the wrong time. VIF and station slot bitmaps must stay synchronized with firmware objects. Channel reset paths must drain WMI/TX/RX before hardware reset to avoid stale completions. Monitor mode is special and limited to one firmware interface. Several WMI command macros reuse a local `ret`; changes around those macros can accidentally skip error handling.

## Test Signals

Exercise mac80211 start/stop, add/remove station/AP/mesh/IBSS/monitor interfaces, concurrent two-interface combinations, association/disassociation, channel change and off-channel scan, software scan start/complete, power-save transitions, suspend-like stop/start, key install/removal for supported ciphers, AMPDU start/stop/operational transitions, bitrate mask updates, beacon enable/disable, TSF get/set/reset, and hot unplug during active callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_txrx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_txrx.c

## Purpose

`htc_drv_txrx.c` implements the ath9k HTC host TX and RX data path. It builds firmware TX headers, maps mac80211 queues to firmware endpoints, tracks outstanding SKBs by slots and cookies, consumes firmware TX status events, handles TX cleanup/timeouts, configures TX queues, computes RX filters, validates firmware RX status headers, and hands accepted frames to mac80211.

## Important APIs, Types, and Functions

TX queue pressure is managed by `ath9k_htc_check_stop_queues()` and `ath9k_htc_check_wake_queues()`, which count outstanding host frames and stop/wake mac80211 queues around `ATH9K_HTC_TX_THRESHOLD`. `ath9k_htc_tx_get_slot()` and `ath9k_htc_tx_clear_slot()` allocate cookies from `priv->tx.tx_slot`.

`ath9k_htc_tx_start()` is the main transmit entry after `htc_drv_main.c` has selected a slot. It resolves firmware VIF and station indices, dispatches to `ath9k_htc_tx_data()` for data frames or `ath9k_htc_tx_mgmt()` for management frames, then sends through `htc_send()`. `ath9k_htc_tx_data()` fills `struct tx_frame_hdr` with node, VIF, cookie, data type, TID, RTS/CTS flags, crypto key type/index, and endpoint selection. `ath9k_htc_tx_mgmt()` fills `struct tx_mgmt_hdr` and handles probe response TSF adjustment.

Completion handling uses two stages. `ath9k_htc_txep()` is called by the HTC endpoint TX callback after HIF submission completes; successful SKBs are queued per endpoint, failed SKBs go to `tx_failed` and a tasklet. Later, WMI firmware status enters `ath9k_htc_txstatus()`, which locates the matching queued SKB by endpoint and cookie via `ath9k_htc_tx_get_packet()`. `ath9k_htc_tx_process()` strips firmware headers, maps status flags into `ieee80211_tx_info`, clears queued counters/slots, removes padding, and calls `ieee80211_tx_status_skb()`.

RX initialization and cleanup are `ath9k_rx_init()` and `ath9k_rx_cleanup()`. `ath9k_htc_rxep()` places incoming endpoint SKBs into an available `ath9k_htc_rxbuf` and schedules `ath9k_rx_tasklet()`. `ath9k_rx_prepare()` validates the firmware RX header, converts `struct ath_htc_rx_status` to `struct ath_rx_status`, processes errors, rate, RSSI, decrypt status, spectral/PHY errors, and fills mac80211 `ieee80211_rx_status`.

## Control Flow

The TX path is: mac80211 callback reserves padding and a TX slot, `ath9k_htc_tx_start()` prepends a firmware header, `htc_send()` prepends an HTC frame header and sends over HIF, `ath9k_htc_txep()` queues the SKB by endpoint after host submission, firmware later emits WMI TX status, `ath9k_htc_txstatus()` matches status to SKB, and `ath9k_htc_tx_process()` returns final status to mac80211. If the status arrives before the SKB is queued, the status is saved in `pending_tx_events` and retried by `ath9k_htc_tx_cleanup_timer()`.

The drain path sets `ATH9K_HTC_OP_TX_DRAIN`, stops HTC, kills WMI and failed-TX tasklets, drains every endpoint queue through `ath9k_htc_tx_process(..., NULL)`, frees pending TX events, and clears the drain flag. The cleanup timer scans pending status events and status-pending endpoint queues for timeout, returning timed-out frames to mac80211 with failure status.

The RX path is: HTC endpoint callback receives an SKB, claims a free RX buffer under `rxbuflock`, marks it in process, schedules the tasklet, validates/prepares the frame, copies RX status into the skb control block, queues PS work for beacons when PS is enabled, calls `ieee80211_rx()`, and requeues the RX buffer.

## State and Persistence Behavior

Persistent TX state includes endpoint SKB queues, the failed queue, queued count, queue stop/drain flags, slot bitmap, pending TX status list, per-AC queue statistics, and cleanup timer timestamps in `ath9k_htc_tx_ctl`. RX state is a fixed list of `ATH9K_HTC_RXBUF` host buffers with `in_process` and `skb` fields plus an `initialized` gate. Firmware station/VIF indices are embedded in each firmware TX header, and TX status uses endpoint/cookie matching rather than pointer identity.

## Dependencies and Integration Points

The file depends on mac80211 SKB control blocks, HTC endpoint callbacks, WMI TX status events, firmware header definitions from `htc.h`, shared ath9k queue APIs, common RX post-processing helpers, spectral scan helpers, and hardware RX filter/register functions from `hw.c`.

## Risks

The TX completion path is vulnerable to ordering races between HIF completion and WMI status, which is why `pending_tx_events` exists. Cookie reuse must be bounded by slot clearing; premature slot reuse can misattribute TX status. Queue counters must be decremented exactly once or queues can stick stopped. RX validation must reject short or inconsistent firmware-reported lengths before `skb_pull()`. RX cleanup and init are explicitly marked with a locking FIXME, so teardown during endpoint activity is a sensitive area. Timer callbacks, tasklets, and drain paths all touch the same queues and lists.

## Test Signals

Useful tests include high-throughput TX to force queue stop/wake, injected HIF submission failure, delayed or reordered TX status, TX timeout cleanup, AMPDU start and status mapping, management frame TX status, CAB/multicast traffic, malformed or short RX frames, invalid RX key indexes, PHY error/spectral frames, PS beacons scheduling `ps_work`, RX init failure cleanup, and hot unplug while endpoint queues contain SKBs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_txrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_hst.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_hst.c

## Purpose

`htc_hst.c` is the host-side HTC protocol implementation for ath9k HTC. It wraps and unwraps HTC frame headers, manages service endpoint connection, processes firmware control messages, dispatches non-control frames to endpoint callbacks, reports firmware panic messages, and connects the generic HTC transport layer to ath9k device probe/deinit.

## Important APIs, Types, and Functions

`htc_issue_send()` is the low-level send helper. It pushes `struct htc_frame_hdr`, fills endpoint ID, flags, big-endian payload length, zeroed control bytes, and calls the HIF `send()` callback on the endpoint upload pipe. `htc_send()` obtains the endpoint from `HTC_SKB_CB(skb)->epid`; `htc_send_epid()` sends to an explicit endpoint.

Endpoint setup is performed by `htc_connect_service()`. It selects a temporary unused endpoint slot, fills service ID, queue depth, callback table, and upload/download pipe IDs from `service_to_ulpipe()`/`service_to_dlpipe()`, sends an `HTC_MSG_CONNECT_SERVICE_ID` message on endpoint 0, waits for `cmd_wait`, validates `conn_rsp_epid`, and returns the firmware-assigned endpoint. `htc_process_conn_rsp()` moves the temporary endpoint metadata into the endpoint ID returned by firmware.

Target setup uses `htc_config_pipe_credits()`, `htc_setup_complete()`, and `htc_init()`. These send control messages and wait for HIF TX completion to signal command completion through `ath9k_htc_txcompletion_cb()`. Target readiness is processed by `htc_process_target_rdy()`, which records credit size, reserves endpoint 0 for `HTC_CTRL_RSVD_SVC`, increments `tgt_ready`, and completes `target_wait`.

Receive dispatch is `ath9k_htc_rx_msg()`. It validates frame length and endpoint, recognizes firmware panic endpoint `0x99`, handles endpoint 0 control messages (`HTC_MSG_READY_ID` and `HTC_MSG_CONNECT_SERVICE_RESPONSE_ID`), trims trailers for data endpoints, strips the HTC header, and invokes endpoint RX callbacks.

Allocation and bridge functions are `ath9k_htc_hw_alloc()`, `ath9k_htc_hw_free()`, `ath9k_htc_hw_init()`, and `ath9k_htc_hw_deinit()`.

## Control Flow

The transport starts with `ath9k_htc_hw_alloc()`, which allocates `struct htc_target`, initializes completions, stores HIF/device pointers, and assigns endpoint 0 pipe IDs from the HIF descriptor. Firmware later sends a ready message; `ath9k_htc_rx_msg()` dispatches it to `htc_process_target_rdy()`, unblocking probe.

Service connection is request/response over endpoint 0. The host first reserves a local endpoint as temporary state, sends the service connection message with firmware pipe IDs, and waits up to one second. The response handler validates firmware endpoint ID, finds the temporary endpoint by service ID, clears that slot, copies metadata to the firmware endpoint, records `conn_rsp_epid`, and completes `cmd_wait`.

Data and WMI frames bypass control-message parsing. RX is delivered to the endpoint callback registered by the service owner, while TX completion removes the HTC header and invokes endpoint TX callbacks or frees the SKB.

## State and Persistence Behavior

`struct htc_target` owns endpoint metadata, HIF callbacks, completions, `conn_rsp_epid`, target credits, credit size, `htc_flags`, and target-ready count. Endpoint state persists after service connection and contains service ID, callbacks, queue depth, max message length, and pipe IDs. `htc_flags` is a transient command-completion discriminator for credit config and setup-complete messages. SKB ownership changes at callback boundaries: control SKBs are freed by HTC code; service RX SKBs are handed to endpoint owners; service TX SKBs are handed to endpoint TX callbacks or freed if no callback exists.

## Dependencies and Integration Points

This file depends on `htc_hst.h` protocol structures, `htc.h` private driver definitions, Linux SKB APIs, completions, endian helpers, device logging, and HIF callbacks supplied by USB transport. It integrates upward with `ath9k_htc_probe_device()` and `ath9k_htc_disconnect_device()` and laterally with WMI/TX/RX endpoint callbacks.

## Risks

Length validation is essential because firmware controls RX frame contents. Endpoint connection state is temporarily keyed by service ID and can be confused if duplicate services are connected concurrently. Some timeout/error paths after successful send do not free the SKB because ownership was transferred to HIF; that is intentional but sensitive to HIF semantics. `htc_flags` allows only one pending setup/credit operation style at a time. Firmware panic reporting reads firmware-provided structures and should preserve size checks. Trailer trimming trusts `control[0]` after only broad frame validation.

## Test Signals

Exercise firmware ready handling, service connection success and failure responses, endpoint ID boundary checks, setup-complete and credit-config timeouts, malformed endpoint 0 messages, data endpoint dispatch, missing endpoint callbacks, HIF TX failure, firmware panic patterns, trailer frames, and hot-unplug deinit while target state exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_hst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_hst.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_hst.h

## Purpose

`htc_hst.h` declares the host-side HTC transport contract used by ath9k HTC. It defines HIF transport callbacks, HTC endpoint IDs, wire-format control messages, service IDs, endpoint callback structures, target state, and the public host transport APIs consumed by the USB HIF, WMI, and ath9k HTC driver layers.

## Important APIs, Types, and Functions

`enum ath9k_hif_transports` currently contains `ATH9K_HIF_USB`, making USB the supported HIF transport. `struct ath9k_htc_hif` describes the transport implementation: list linkage, transport name, control pipe IDs, `start`, `stop`, `sta_drain`, and `send` callbacks.

`enum htc_endpoint_id` defines endpoint 0 through endpoint 8 plus `ENDPOINT_MAX = 22` and `ENDPOINT_UNUSED = -1`. Endpoint 0 is reserved for HTC control. `struct htc_frame_hdr` is the packed wire header with endpoint ID, flags, big-endian payload length, and four control bytes. `HTC_FLAGS_RECV_TRAILER` indicates a trailer exists.

Control messages include `struct htc_ready_msg`, `struct htc_config_pipe_msg`, `struct htc_conn_svc_msg`, `struct htc_conn_svc_rspmsg`, and `struct htc_comp_msg`, with message IDs in `enum htc_msg_id`. Firmware panic formats are `struct htc_panic_bad_vaddr` and `struct htc_panic_bad_epid`.

`struct htc_ep_callbacks` carries endpoint owner callbacks for TX completion and RX delivery. `struct htc_endpoint` stores service ID, callbacks, max queue depth, max message length, and pipe IDs. `struct htc_target` is the main transport object: HIF/device pointers, driver private pointer, endpoint table, completions, list linkage, last connect response endpoint, credits, credit size, flags, and atomic ready count.

Service IDs are built with `MAKE_SERVICE_ID()` and include reserved HTC control plus WMI control, beacon, CAB, UAPSD, management, and four data access categories. Public functions include `htc_init()`, `htc_connect_service()`, `htc_send()`, `htc_send_epid()`, `htc_stop()`, `htc_start()`, `htc_sta_drain()`, RX/TX callbacks from HIF, and target allocation/init/deinit helpers.

## Control Flow

The header describes a layered flow: HIF allocates and starts an `htc_target`; endpoint 0 receives ready and connect responses; service owners connect WMI/data services by service ID; data senders attach endpoint IDs in `HTC_SKB_CB`; HIF receive calls `ath9k_htc_rx_msg()`; HTC dispatches control messages internally and service frames to registered endpoint callbacks.

## State and Persistence Behavior

The state defined here persists for the life of the USB device. `htc_target.endpoint[]` is the routing table for service callbacks and pipe IDs. `target_wait` and `cmd_wait` serialize target readiness and command responses. `credits` and `credit_size` store transport flow-control parameters discovered/configured during startup. `htc_flags` stores in-flight operation bits for setup and pipe credit commands. The callback structures preserve the owner pointer used to return SKBs to `struct ath9k_htc_priv` paths.

## Dependencies and Integration Points

The header depends on Linux list, completion, atomic, device, SKB, and endian types through included driver headers. It integrates with USB HIF transport, `htc_hst.c`, WMI service setup, TX/RX code, and device probe/deinit functions in `htc_drv_init.c`.

## Risks

All wire structs are packed and endian-tagged; any change to fields or byte order must match firmware. `ENDPOINT_MAX` is larger than the explicitly named endpoint constants, so loops and bounds checks must use `ENDPOINT_MAX` rather than assuming only 0 through 8. Callback ownership is not self-describing; endpoint owners must know whether they receive an HTC-stripped SKB and whether they must free it. Service IDs and pipe IDs are firmware ABI, not local policy.

## Test Signals

Compile-time structure layout compatibility, endpoint bounds checks, service ID mapping, callback invocation for every WMI service, target ready completion, command completion, and USB transport start/stop/drain behavior are the main signals. ABI-sensitive changes should be tested against real firmware or firmware protocol emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_hst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hw-ops.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hw-ops.h

## Purpose

`hw-ops.h` is the inline dispatch layer for ath9k hardware-family operations. It gives shared driver code stable function names while routing implementation details through `struct ath_hw_ops` and `struct ath_hw_private_ops`, which are populated by AR9002/AR9003 family attach code.

## Important APIs, Types, and Functions

The public hardware wrappers include PCI power-save, RX enable, descriptor linking, calibration, interrupt status, TX descriptor setup/status processing, duration lookup, antenna diversity configuration, and tx99 test helpers. These call `ath9k_hw_ops(ah)->...`.

Private hardware wrappers include hang checks, PHY frequency and spur handling, RF register setup, baseband init, channel register programming, INI processing, OLC init, RF mode/delta slope, RF bus request/done, chainmask restore, ANI control, noise-floor reads, init calibration, calibration setup, fast channel change, radar params, calibration settings, PLL control computation, mode gain register init, and ANI INI cache. These call `ath9k_hw_private_ops(ah)->...`.

Several wrappers are conditional or nullable. `ath9k_hw_tx99_set_txpower()`, BT antenna diversity, AIC support, `ath9k_olc_init()`, `ath9k_hw_set_rf_regs()`, chainmask restore, radar params, mode gain init, and ANI INI cache guard optional callbacks.

## Control Flow

The flow is simple but important: `ath9k_hw_init()` attaches family-specific ops, then the rest of the hardware core and driver call these static inline wrappers. For example, `ath9k_hw_reset()` calls private wrappers for INI processing, RF mode/frequency, delta slope, spur mitigation, baseband init, calibration, and radar configuration without needing to branch on chip family at every call site.

## State and Persistence Behavior

This header stores no state directly. Its behavior depends entirely on function pointers embedded in `struct ath_hw`: `ah->ops` and `ah->private_ops`. The correctness of every wrapper therefore depends on attach-time initialization matching the detected MAC revision and on optional callbacks being checked before use.

## Dependencies and Integration Points

It includes `hw.h` and is included by `hw.c` plus other ath9k code that needs hardware-family operations. It integrates with `ar9002_hw_attach_ops()`, `ar9003_hw_attach_ops()`, PHY attach helpers, calibration attach helpers, and optional BT coexistence support.

## Risks

Most wrappers do not check for NULL callbacks because the attach path is expected to provide mandatory operations. A missing mandatory function pointer becomes a crash at first use, often during reset or channel change. Optional wrappers must remain guarded. Since these are static inline functions, changes can affect many call sites at compile time and may not have a single symbol to trace at runtime. The division between public and private ops is a maintenance boundary; exposing private wrappers broadly makes chip-family abstractions easier to violate.

## Test Signals

Test by probing every supported AR9xxx family path, resetting and changing channels, running calibration/ANI, starting RX/TX, reading interrupts, and exercising optional features such as BT coexistence, tx99, antenna combining, radar/DFS, and fast channel change. Build coverage should include configurations with and without `CONFIG_ATH9K_BTCOEX_SUPPORT`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hw-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hw.c

## Purpose

`hw.c` is the shared ath9k hardware core for AR5008/AR9001/AR9002/AR9003-family devices, including HTC USB users. It detects hardware revisions, attaches family ops, initializes EEPROM/regulatory/capability state, performs reset and channel change, manages power modes, programs timing, beacon, DMA, interrupt, GPIO, RX filter, TX power, TSF, generic timer, and hardware-name behavior.

## Important APIs, Types, and Functions

Initialization is driven by `ath9k_hw_init()`, which validates device ID, calls `__ath9k_hw_init()`, and initializes dynamic ACK. `__ath9k_hw_init()` reads revisions, validates supported MAC versions, sets reset/WA defaults, attaches family ops, wakes the chip, initializes PHY/calibration settings, disables PCIe on non-PCIe devices, initializes EEPROM and ANI, fills capabilities, reads MAC address, initializes hang checks, and marks `ATH_HW_INITIALIZED`.

Reset and channel change are handled by `ath9k_hw_reset()`, `ath9k_hw_do_fastcc()`, `ath9k_hw_channel_change()`, `ath9k_hw_chip_reset()`, `ath9k_hw_set_reset_reg()`, `ath9k_hw_set_reset()`, and `ath9k_hw_set_reset_power_on()`. The reset path preserves/restores TSF, LED state, antenna defaults, opmode, calibration data, noise floor history, queue state, interrupt masks, global timing, DMA, baseband, chainmask, descriptors, BT/MCI state, GPIO overrides, DFS radar params, and noise-floor calibration.

Power management is exposed as `ath9k_hw_setpower()` with modes `ATH9K_PM_AWAKE`, `ATH9K_PM_FULL_SLEEP`, and `ATH9K_PM_NETWORK_SLEEP`. Helpers program force-wake, RTC reset/status, STA power-save bits, autosleep/MCI behavior, and AR_WA workarounds.

General exported hardware APIs include `ath9k_hw_wait()`, `ath9k_hw_synth_delay()`, INI array read/write helpers, `ath9k_hw_computetxtime()`, `ath9k_hw_get_channel_centers()`, `ath9k_hw_init_global_settings()`, RX filter get/set, PHY/hardware disable, TX power application/limits, opmode, multicast filters, association ID writes, TSF get/set/reset, 20/40 MAC mode, beacon timers, station beacon timers, NAV/alive checks, GPIO request/get/set/free, antenna selection, generic timer alloc/start/stop/free/ISR, and `ath9k_hw_name()`.

## Control Flow

Initialization first establishes what chip is present and which operation table should be used. After reset and wake, EEPROM initialization populates board-specific data, capability fill reads regulatory, band, chainmask, GPIO, crypto, HT, autosleep, EDMA, LDPC, SGI, antenna diversity, MCI/RTT/PAPRD/WoW support, and descriptor lengths.

`ath9k_hw_reset()` is the central operational flow. It wakes hardware, saves current NF if possible, installs/reset calibration data for the requested channel, tries fast channel change if requested, handles MCI reset choreography, saves state that a reset would clobber, marks PHY inactive, applies AR9271 first-reset sequencing, resets the chip and PLL, restores TSF with elapsed-time compensation, processes INI/register tables, configures RF mode/frequency, applies EEPROM board values and TX power, restores opmode and queues, initializes interrupts/QoS/timing/DMA/baseband/descriptors, runs initial calibration, restarts generic timers, re-enables BT/MCI/PAPRD/noise-floor/radar/GPIO behaviors, and returns status.

Fast channel change is intentionally conservative. It rejects fullsleep, missing current channel, same channel, half/quarter rates, incompatible band/mode flags, dead hardware, pending TX queues, and missing calibration on AR9462. If allowed, it uses RF bus locking, family fast channel ops, board-value refresh when needed, baseband init, and NF calibration without a full chip reset.

## State and Persistence Behavior

`hw.c` mutates most fields in `struct ath_hw`: revision and capability data, EEPROM ops/data, current channel, power mode, chip sleep state, calibration pointers and flags, noise floor, opmode, interrupt masks, queue configs, timing values, chainmasks, GPIO masks/values, WA registers, generic timers, BT/MCI state, descriptor lengths, radar config, TSF, and hardware workarounds. Some state is persistent across resets and deliberately restored, such as TSF, LED config, default antenna, `WARegVal`, opmode, BSSID mask, global TX timeout, GPIO overrides, and calibration history when channel-compatible.

## Dependencies and Integration Points

The file depends on register definitions, PHY/MAC helpers, EEPROM ops, ANI/calibration, BT coexistence/MCI, dynamic ACK, regulatory helpers, Linux GPIO, firmware and device APIs, and family-specific AR9002/AR9003 attach code. It is used by PCI, platform, and USB/HTC drivers through `struct ath_ops` register callbacks, so register access may be direct MMIO or firmware-mediated WMI depending on bus.

## Risks

Reset sequencing is highly chip-specific; small ordering changes can break certain revisions. Register reads during sleep are avoided through cached values such as `WARegVal`, and violating that assumption can hang hardware. Fast channel change must not proceed with pending TX or incompatible calibration. Capability fill depends on EEPROM correctness and device revision macros. Power transitions interact with MCI/BT and autosleep; wrong force-wake handling can leave the chip inaccessible. GPIO paths split between WMAC and SoC GPIO domains. Generic timer callbacks run from interrupt context and must tolerate missing timer slots. USB/HTC users depend on all register ops being safe over WMI latency.

## Test Signals

Test probe/reset on representative AR5416, AR9280/9285/9287/9271, AR9300, AR9330/9340, AR9462/9565, and SoC variants; channel changes with and without fastcc; half/quarter/HT40 timing; sleep/wake/network sleep loops; TX/RX after reset; EEPROM/regulatory band disable cases; rfkill GPIO; TSF continuity across reset; beacon timers in AP/STA; generic timer interrupts; DFS/radar-enabled channels; BT/MCI coexistence; hot-unplug paths that set `AH_UNPLUGGED`; and WMI-backed HTC register operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hw.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hw.h

## Purpose

`hw.h` is the central hardware contract for ath9k. It defines supported Atheros device IDs, register access macros, timing constants, capability flags, channel/calibration/beacon/power/timer/radar data structures, operation tables, the full `struct ath_hw` state container, bus callbacks, inline accessors, and exported hardware-core function prototypes.

## Important APIs, Types, and Functions

The top-level constants enumerate PCI/PCIe/SoC/USB-capable AR9xxx device IDs and hardware limits such as `ATH9K_NUM_CHANNELS`, `ATH9K_NUM_QUEUES`, `AR_KEYTABLE_SIZE`, TX power limits, wait timeouts, and WoW pattern limits.

Register macros `REG_WRITE`, `REG_READ`, `REG_READ_MULTI`, `REG_RMW`, buffered write/RMW helpers, `SM`, `MS`, field helpers, and INI array helpers abstract bus-specific register operations through `ah->reg_ops`. This is what lets HTC USB supply WMI-backed register operations while PCI code can use MMIO-style operations.

Major types include `enum ath9k_hw_caps`, `struct ath9k_hw_capabilities`, `enum ath9k_int`, `struct ath9k_hw_cal_data`, `struct ath9k_channel`, channel flag macros, `enum ath9k_power_mode`, `struct ath9k_beacon_state`, `struct chan_centers`, `struct ath9k_hw_version`, generic timer structs, `struct ath_hw_antcomb_conf`, `struct ath_hw_radar_conf`, `struct ath_hw_private_ops`, `struct ath_hw_ops`, `struct ath_spec_scan`, `struct ath_nf_limits`, `struct ath_bus_ops`, and `struct ath_hw`.

`struct ath_hw` is the persistent state hub. It contains register ops, device/mac80211/common pointers, revision, config, capabilities, channel table, EEPROM storage and ops, software crypto flags, bus/revision flags, RF kill, reset/power state, calibration data and measurements, opmode, TX queues and interrupts, private/public ops tables, INI arrays, generic timers, TX status ring, watchdog state, PAPRD state, WA registers, MCI/BT fields, EEPROM blobs, dynamic ACK, TPC, MSI, and more.

The prototypes export initialization, reset, GPIO, general operation, power, generic timers, PHY utilities, family-specific attach helpers, ANI, timeout setters, BT coexistence wrappers, WoW wrappers, and hardware-name reporting.

## Control Flow

The header establishes how code should move through the hardware layer. Bus code allocates `struct ath_hw`, fills `reg_ops`, `bus_ops`, device IDs, and platform hooks, then calls `ath9k_hw_init()`. Family attach code populates `private_ops` and `ops`, and runtime code calls prototypes or `hw-ops.h` wrappers to reset, configure channels, start RX/TX, handle calibration, and enter power states.

## State and Persistence Behavior

State is explicitly centralized in `struct ath_hw` and `struct ath_common`. The file distinguishes board-derived persistent state, runtime state, reset-preserved state, and optional feature state. Register access itself is stateful through optional buffering callbacks. Channel/calibration state is preserved per `struct ath9k_hw_cal_data` when channel-compatible. Capability bits gate runtime features and must be filled before mac80211 capability publication.

## Dependencies and Integration Points

The header includes Linux networking, delay, I/O, and firmware headers plus ath9k local `mac.h`, `ani.h`, `eeprom.h`, `calib.h`, `reg.h`, `reg_mci.h`, `phy.h`, `btcoex.h`, `dynack.h`, and common regulatory definitions. It is consumed by shared hardware code, HTC code, PCI/platform drivers, family-specific PHY/MAC/calibration files, common ath helpers, debugfs, BT coexistence, WoW, and spectral scan code.

## Risks

This header is a broad ABI inside the driver. Changing `struct ath_hw`, ops tables, or macros affects many files and chip families. Register macros evaluate through function pointers, so callers must not assume MMIO timing or sleepability; HTC paths can use WMI. Bitmask constants and structure sizes must match hardware and firmware expectations. Conditional compilation can hide missing operations in some configs. Adding fields to `struct ath_hw` without initialization in every bus path can leave reset or power logic reading garbage.

## Test Signals

Build all ath9k configurations, including HTC, PCI, BT coexistence, WoW, RFKILL, and debugfs. Probe multiple chip families, verify capabilities published by mac80211, run register read/write buffer paths, reset/channel/power operations, GPIO/rfkill, generic timers, calibration/ANI, spectral scan, and WoW where enabled. Static analysis should check ops-table mandatory callbacks and structure initialization paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/hw.h -->
