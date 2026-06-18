# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7603/beacon.c

## Purpose
MT7603 beacon and buffered broadcast/multicast handling around pre-TBTT interrupts. It refreshes beacon frames, prepares CAB traffic, programs beacon timers, and includes recovery for stuck beacon queues.

## Important APIs, Types, And Functions
- `struct beacon_bc_data` collects buffered broadcast/multicast SKBs, per-interface tail pointers, and frame counts.
- `mt7603_mac_stuck_beacon_recovery()` periodically toggles DMA scheduler/TMAC/ARB state when the beacon queue appears stuck.
- `mt7603_update_beacon_iter()` obtains a fresh beacon via `ieee80211_beacon_get()`, flushes target beacon/BMC hardware queues through `MT_DMA_FQCR0`, and queues it on `MT_TXQ_BEACON`.
- `mt7603_add_buffered_bc()` drains mac80211 buffered BC/MC frames, marks sequence assignment and More Data, and stores counts.
- `mt7603_pre_tbtt_tasklet()` is the pre-TBTT tasklet that flushes old CAB/beacon frames, updates beacons, checks CSA completion, sends CAB frames, and starts hardware CAB release.
- `mt7603_beacon_set_timer()` enables/disables per-BSS beacon masks, TBTT/PRE_TBTT registers, beacon queue opmode, MAC IRQ3 mask bits, and sub-BSS timing.

## Control Flow
AP beaconing is enabled from `bss_info_changed()` through `mt7603_beacon_set_timer()`. Hardware PRE_TBTT triggers `mt7603_irq_handler()`, which schedules the tasklet. The tasklet skips offchannel operation, flushes old beacon/CAB content, increments stuck-beacon counters if the beacon queue remains occupied, refreshes beacon frames under the beacon queue lock, checks CSA, drains up to a small batch of buffered BC/MC frames, queues them to CAB, writes per-BSS CAB counts, and starts CAB transmission.

## State And Persistence
State lives in `dev->mt76.beacon_mask`, `dev->mt76.beacon_int`, `dev->beacon_check`, TX queue occupancy, per-interface beacon bits, and hardware TBTT/CAB registers. SKBs are transient and owned by TX queues after enqueue.

## Dependencies And Integration Points
Depends on mac80211 beacon/CAB APIs, mt76 TX queue helpers, mt7603 register definitions, tasklets, and CSA helpers from the shared mt76 mac80211 layer. It integrates with `core.c` IRQ handling and `main.c` BSS change callbacks.

## Risks
Tasklet concurrency with interface removal and channel changes is handled by explicit tasklet disable in callers; missing that can race with queue/register updates. If `MT_DMA_FQCR0` does not clear, the watchdog is forced through `beacon_check`. CAB batching is capped, so unusual buffering patterns need validation. CSA returns early after beacon update to avoid sending CAB during channel switch.

## Test Signals
Run AP mode with one and multiple BSSIDs, buffered multicast under sleeping stations, CSA/channel switch, interface removal during beaconing, and offchannel scans while AP is active. Monitor reset cause "Beacon stuck", PRE_TBTT/TBTT interrupts, CAB delivery, and absence of stale More Data flags.
