# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00dev.c

## Purpose
Implements the shared rt2x00 device lifecycle and interrupt-context data path glue. It enables/disables radio, schedules deferred interface work and powersave sleep, handles beacon/TBTT events, processes DMA start/done, converts TX/RX completions into mac80211 status, builds supported rates/channels, registers `ieee80211_hw`, initializes queues/work/tasklets/debug/LED/rfkill, and handles remove/suspend/resume.

## Important APIs, Types, And Functions
Exports `rt2x00lib_get_bssidx()`, `rt2x00lib_enable_radio()`, `rt2x00lib_disable_radio()`, beacon/TBTT/DMA/TX/RX completion helpers, `rt2x00_supported_rates`, `rt2x00lib_set_mac_address()`, `rt2x00lib_start()`, `rt2x00lib_stop()`, `rt2x00lib_probe_dev()`, `rt2x00lib_remove_dev()`, `rt2x00lib_suspend()`, and `rt2x00lib_resume()`. Important private helpers include BAR status matching, TX status filling, RX power-save/TIM parsing, RX signal-rate decoding, hardware mode setup, and common initialization/uninitialization.

## Control Flow
Probe initializes locks, workqueue, hrtimer, device-present flag, vif private size, address mask, hardware capabilities via chip `probe_hw`, queue allocation, mac80211 registration, link tuner, LEDs, debugfs, and rfkill. Start loads firmware, initializes queues/hardware, resets interface counters, enables radio, starts queues/tuner/watchdog, and marks started. Stop disables radio and clears counters. TX done unmaps DMA, restores skb headroom/L2 padding/IV, dumps debug frames, derives ACK/rate/AMPDU status, reports to mac80211, frees non-mac80211 skbs, clears entries, and unpauses queues. RX done allocates a replacement skb, unmaps the filled skb, asks chip code to fill `rxdone_entry_desc`, validates size, restores crypto or padding, trims, maps signal to rate index, checks TIM powersave and BAR/BA correlation, updates link/debug stats, fills `ieee80211_rx_status`, submits to mac80211, and requeues the entry.

## State And Persistence
Owns most persistent `rt2x00_dev` state: flags, counters, queue objects, txstatus FIFO, workqueue, BAR list, low-level stats, firmware pointer, channel/rate tables, debug/LED registrations, rfkill polling, and interface counts. Suspend clears `DEVICE_STATE_PRESENT`, uninitializes queues/hardware, suspends LEDs/debugfs, and best-effort sleeps device. Resume recreates debugfs/LED state and marks present; mac80211 drives reconfiguration.

## Dependencies And Integration Points
Integrates with mac80211 RX/TX APIs, rt2x00 queue layer, chip `rt2x00lib_ops`, firmware loader, debugfs, LEDs, rfkill, workqueue/tasklet/hrtimer/kfifo infrastructure, OF MAC address lookup, and RT2800 transport callbacks. Bus drivers call `rt2x00lib_probe_dev()` and `remove_dev()`.

## Risks
This file is concurrency-heavy: tasklets, workqueue, mac80211 callbacks, suspend/remove, and timer paths all inspect state flags. TX done must restore skb shape exactly for mac80211. RX done must never read corrupted descriptor sizes. BAR status matching uses RCU plus spinlock and can misattribute BA if tuple matching is incomplete. Probe/remove unwind spans many subsystems and must tolerate partial initialization. Resume relies on mac80211 reconfiguration after only marking device present.

## Test Signals
Full probe/remove fault injection, firmware load failures, TX/RX status under load, BAR/BA aggregation, AP beacon buffering, powersave TIM sleep/wake, rfkill, restart_hw, suspend/resume, debugfs/LED registration errors, queue threshold wakeups, malformed RX sizes, and lockdep/KASAN/RCU diagnostics.
