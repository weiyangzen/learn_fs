# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt792x_mac.c

## Purpose
This file provides shared MT792x MAC maintenance: periodic survey/MIB work, timing/coverage programming, MIB/stat accumulation, RX WCID selection, association RSSI tracking, channel accounting, reset scheduling, band initialization, and runtime PM wake/sleep workers.

## Important APIs, Types, And Functions
Exports include `mt792x_mac_work()`, `mt792x_mac_set_timeing()`, `mt792x_mac_update_mib_stats()`, `mt792x_rx_get_wcid()`, `mt792x_mac_assoc_rssi()`, `mt792x_mac_reset_counters()`, `mt792x_update_channel()`, `mt792x_reset()`, `mt792x_mac_init_band()`, `mt792x_pm_wake_work()`, and `mt792x_pm_power_save_work()`.

## Control Flow
Periodic MAC work takes the mutex, updates survey counters, refreshes MIB every second run, releases the mutex, checks TX status, and reschedules itself. Timing setup temporarily disables TX/RX arbitration, programs CCK/OFDM timeouts plus coverage offset, SIFS/slot/EIFS/RIFS, selects CF-end rate, and reenables arbitration. MIB update accumulates counters for FCS/ACK/BA/RTS, TX/RX MPDU/AMPDU, beamforming, AMSDU, and aggregation buckets. Channel update wakes hardware, samples busy/TX/RX/OBSS time, clears OBSS airtime, and schedules power save. PM wake work reacquires driver ownership, dequeues pending SKBs, schedules NAPI or SDIO worker, restarts MAC work, wakes mac80211 queues, and wakes PM waiters. PM save work avoids sleeping during scanning, firmware assert, mutex-held register access, or recent activity; otherwise it gives ownership to firmware and cancels MAC work.

## State And Persistence
State includes `phy->mib`, aggregation stats, survey time/channel state, RSSI EWMA, coverage/slottime/noise, PM awake/doze counters, pending SKB queues, reset work state, firmware assertion flag, and hardware timing/MIB registers.

## Dependencies And Integration Points
It integrates with mt76 survey/TX status, mac80211 interface iteration, connac PM, MT792x register definitions, DMA/NAPI workers, and chip-specific reset work.

## Risks
Register access during PM sleep is guarded but still timing-sensitive. MIB counters are accumulated by reading clear-on-read or rolling hardware registers; missed reads or reset races skew stats. Multicast RX WCID remapping assumes station/vif links remain valid. Power-save scheduling must not sleep during scans or while the mutex protects active register transactions.

## Test Signals
Survey/airtime accuracy, coverage-class changes, association RSSI, stats under traffic, runtime PM wake/sleep cycles, reset work scheduling, scan while idle, and lockdep around PM mutex/register access validate this file.
