# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/scan.c

## Purpose
`scan.c` implements firmware hardware scanning for the DVM driver. It builds `REPLY_SCAN_CMD` payloads, handles scan notifications, maintains scan state bits, supports cancellation and watchdog completion, performs internal short passive scans used as RF reset, and applies deferred RXON/power settings when scans finish.

## Important APIs, Types, And Functions
- `iwl_scan_initiate()` is the main entry point for normal and internal scan start.
- `iwlagn_request_scan()` allocates/fills `struct iwl_scan_cmd`, including probe request, channel list, dwell times, TX rate, RX chain selection, suspend timing, and PAN updates.
- `iwl_send_scan_abort()`, `iwl_do_scan_abort()`, `iwl_scan_cancel()`, and `iwl_scan_cancel_timeout()` implement asynchronous and timeout-based cancellation.
- `iwl_process_scan_complete()` reconciles scan completion bits, reports completion to mac80211, restarts pending normal scans after internal scans, and calls `iwlagn_post_scan()`.
- `iwl_force_scan_end()` forcibly clears scan state and reports an aborted scan.
- `iwl_rx_reply_scan()`, `iwl_rx_scan_start_notif()`, `iwl_rx_scan_results_notif()`, and `iwl_rx_scan_complete_notif()` handle firmware scan responses and notifications.
- `iwl_setup_rx_scan_handlers()` registers scan notification handlers into `priv->rx_handlers`.
- `iwl_get_active_dwell_time()`, `iwl_get_passive_dwell_time()`, and `iwl_limit_dwell()` compute dwell limits, including association beacon timing constraints.
- `iwl_get_channels_for_scan()` fills the per-channel scan descriptors from `priv->scan_request`.
- `iwl_get_channel_for_reset_scan()` selects a single passive channel for RF reset scans.
- `iwl_fill_probe_req()` builds the probe request template.
- `iwl_internal_short_hw_scan()` queues an internal radio-reset scan.
- `iwl_setup_scan_deferred_work()` and `iwl_cancel_scan_deferred_work()` manage workqueue items.

## Control Flow
Normal scans enter through `iwl_scan_initiate()` under `priv->mutex`. The function rejects scans when RF is not ready, hardware scan is already active, or abort is pending. It sets `STATUS_SCANNING`, records scan type/start/band, calls `iwlagn_request_scan()`, and arms `scan_check` as a watchdog.

`iwlagn_request_scan()` builds the firmware command. For associated scans, it computes suspend timing so firmware periodically returns to the operating channel. For active scans, it inserts the first SSID into the probe request and other SSIDs into `direct_scan` in reverse order. It chooses 1 Mbps CCK or 6 Mbps OFDM on 2.4 GHz depending on `no_cck` and channel mode, always 6 Mbps on 5 GHz, applies Bluetooth coexistence TX flags, selects scan TX antenna, forces RX chains as needed for power-save or full concurrency, fills probe request bytes, fills either the requested channel list or a single radio-reset channel, sets `STATUS_SCAN_HW`, updates PAN params, and sends `REPLY_SCAN_CMD`.

Firmware completion enters through `iwl_rx_scan_complete_notif()`. The handler sets `STATUS_SCAN_COMPLETE`, clears `STATUS_SCAN_HW`, queues `scan_completed` work, and updates Bluetooth traffic status if provided. The work item calls `iwl_process_scan_complete()`, which clears completion/aborting/scanning bits, reports mac80211 scan completion, handles a pending normal scan queued during an internal scan, and calls `iwlagn_post_scan()` if RF is still ready.

Cancellation uses workqueues to avoid doing abort work directly from arbitrary contexts. `iwl_scan_cancel()` queues `abort_scan`. `iwl_bg_abort_scan()` calls `iwl_scan_cancel_timeout()`, which sends abort and waits for `STATUS_SCAN_HW` to clear, then runs completion inline if firmware already completed before the background completion work runs.

Internal RF reset scans are queued through `iwl_internal_short_hw_scan()`, started by `iwl_bg_start_internal_scan()`, and use `IWL_SCAN_RADIO_RESET` with short passive dwell on a valid unused channel.

## State And Persistence Behavior
Scan state is tracked through `priv->status` bits: `STATUS_SCANNING`, `STATUS_SCAN_HW`, `STATUS_SCAN_ABORTING`, and `STATUS_SCAN_COMPLETE`. Additional persistent fields include `scan_type`, `scan_band`, `scan_start`, `scan_start_tsf`, `scan_vif`, `scan_request`, `scan_cmd`, `scan_cmd_size`, and per-band `scan_tx_ant`.

`priv->scan_cmd` is allocated once large enough for firmware channel descriptors plus maximum probe length and reused. Normal scan completion clears `scan_vif` and `scan_request` after reporting to mac80211. Internal scans can leave a mac80211 scan pending and then initiate it after internal completion.

Bluetooth scan status from firmware updates `bt_status`, `bt_traffic_load`, and queues `bt_traffic_change_work`.

## Dependencies And Integration Points
The file depends on mac80211 scan requests, channel flags, supported-band data, firmware scan command structures, DVM command sending, PAN parameter updates from `rxon.c`, post-scan RXON/power reconciliation through `iwlagn_post_scan()`, Bluetooth coexistence state, antenna helpers from rate-scaling definitions, and workqueue infrastructure.

It integrates with `rx.c` through scan RX handler registration. It integrates with RF reset from `rx.c` via `iwl_force_rf_reset()` calling `iwl_internal_short_hw_scan()`. It integrates with RXON because scans defer or alter PAN slots, power settings, and RXON commits.

## Risks And Edge Cases
- `MAX_SCAN_CHANNEL` is enforced only for normal scans with a warning; firmware command sizing depends on this maximum.
- Scan state uses several bits with ordering constraints. Completion sets `STATUS_SCAN_COMPLETE` before clearing `STATUS_SCAN_HW` to avoid abort races.
- `iwl_limit_dwell()` clamps dwell based on beacon intervals and active contexts; arithmetic underflow would be dangerous if limits become smaller than tune time.
- `iwl_fill_probe_req()` must respect available command buffer space; it returns partial length if optional IEs do not fit after warning.
- Internal radio-reset scans pass `vif = NULL`; paths must avoid dereferencing it except where scan type guarantees normal scan.
- PAN params are changed before scan command submission and restored if command submission fails.
- The scan command is reused; if firmware capability max probe length unexpectedly grows, the function refuses rather than reallocating.
- Cancellation can complete inline while a background completion work item is queued; the status-bit protocol prevents double completion.

## Test Signals
Test normal passive and active scans on 2.4 GHz and 5 GHz, with multiple SSIDs, `no_cck`, passive/no-IR channels, associated scans, unassociated scans, P2P/PAN concurrent contexts, power-save scans, Bluetooth full concurrency, aborts, timeout watchdog completion, and internal RF reset scans. Verify mac80211 receives exactly one completion with correct aborted flag. Check that post-scan power, TX power, PAN slots, and pending RXON commits are applied.
