# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/scan.c

## Purpose
Implements shared software-driven hardware-scan orchestration for mt76 PHYs. It serializes one scan request, switches channels, sends probe requests, waits for passive-channel beacons when required, restores the main channel, and reports completion to mac80211.

## Important APIs, Types, And Functions
Exported callbacks are `mt76_hw_scan()`, `mt76_cancel_hw_scan()`, `mt76_abort_scan()`, and `mt76_scan_rx_beacon()`. The central worker is `mt76_scan_work()`. `mt76_scan_complete()` restores channel/offchannel state and calls `ieee80211_scan_completed()`. `mt76_scan_send_probe()` builds probe requests with scan IEs, optional BSSID targeting, no-CCK flag handling, and mt76 TX queueing through the scan vif link WCID.

## Control Flow
`mt76_hw_scan()` selects the correct PHY for multi-radio hardware, rejects concurrent scan/ROC/reset, takes a vif phy link, records the scan request, and schedules work immediately. Each worker run clears beacon-wait state, advances through requested channels, toggles offchannel notification, sets the channel, optionally waits for a beacon on no-IR/radar channels, sends probes for active channels, and reschedules itself for dwell time. Completion or abort restores the main channel and drops the held vif link.

## State And Persistence
Scan state lives in `dev->scan`: request pointer, vif, phy, channel index, current channel, beacon wait/received flags, and `mlink`. The PHY `MT76_SCANNING` bit, `phy->offchannel`, and main channel definition are coordinated with this state. It is transient and explicitly zeroed at completion.

## Dependencies And Integration Points
Integrates with mac80211 scan callbacks, cfg80211 scan request data, mt76 channel-setting helpers, offchannel notifications, vif-link reference helpers, the shared TX path, `scan_lock`, delayed work, and MCU reset state.

## Risks
Race risks center on aborts, beacon wakeups, and reset. The code must avoid completing scans during MCU reset, must restore the main channel after offchannel dwell, and must not use a released vif link. Probe generation assumes `ieee80211_tx_prepare_skb()` succeeds under RCU; failures drop the SKB without more recovery.

## Test Signals
Active and passive scan across 2/5/6 GHz channels, abort while offchannel, scan during association with stations present, multi-radio band selection, no-CCK probe behavior, BSSID-directed scans, reset during scan, and confirmation that queues and channel state return to normal afterward.
