# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/scan.c

Purpose: Implements hardware scan and remain-on-channel support by programming firmware scan requests and converting scan-complete indications into mac80211 callbacks.

Important APIs and functions: `wfx_hw_scan()`, `wfx_cancel_hw_scan()`, `wfx_scan_complete()`, `wfx_remain_on_channel()`, and `wfx_cancel_remain_on_channel()` are mac80211-facing. Work functions `wfx_hw_scan_work()` and `wfx_remain_on_channel_work()` perform serialized scan execution. Helpers update the probe request template and send channel batches with compatible power/NO_IR properties.

Control flow and integration: `wfx_hw_scan()` records the request and schedules work to avoid completing before callback return. Work locks `conf_mutex` and `scan_lock`, aborts an in-progress join via reset, uploads probe template, chunks channels, locks/flushed TX, starts firmware scan, waits for `scan_complete`, stops scan on timeout/cancel, restores output power if needed, unlocks TX, then calls `ieee80211_scan_completed()`. Remain-on-channel hijacks a one-channel scan, notifies ready/expired, and resumes TX.

State and persistence: Per-vif `scan_req`, `scan_complete`, `scan_nb_chan_done`, `scan_abort`, remain-on-channel channel/duration, and work items store scan state. Firmware scan state persists until scan complete or stop.

Dependencies: Depends on HIF scan/stop/template/output-power helpers, station reset/join state, TX lock/flush, mac80211/cfg80211 scan and ROC APIs, and `scan_lock` blocking TX queues.

Risks and test signals: Risks include scan work racing with cancel, firmware scan not stopping, channel batching logic errors, join abort side effects, lock ordering with config/scan locks, and ROC support only for API 3.10+. Tests should cover active/passive scans, multiple SSIDs and IE lengths, cancellation, timeout recovery, join-in-progress abort, output power restore, ROC success/cancel/timeout, and unsupported old API.

Test signals: Source read size: 209 lines, 5964 bytes.
