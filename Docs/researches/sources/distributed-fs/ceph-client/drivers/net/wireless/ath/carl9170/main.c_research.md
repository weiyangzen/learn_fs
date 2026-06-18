# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/carl9170/main.c

## Purpose

`main.c` is the carl9170 mac80211 integration and device lifecycle core. It defines rates/channels/bands, module parameters, mac80211 operations, queue flush/reset behavior, interface management, power save, survey/statistics, key handling, AMPDU state, optional WPS/RNG registration, EEPROM parsing, hardware registration, teardown, and allocation/free routines.

## Important APIs, Types, and Functions

Public entry points are `carl9170_alloc()`, `carl9170_register()`, `carl9170_unregister()`, `carl9170_free()`, `carl9170_restart()`, and `carl9170_ps_check()`. The `carl9170_ops` table wires mac80211 callbacks for start/stop/tx/flush/interface/config/filter/BSS/TSF/key/station/survey/stats/AMPDU/pending frames. Important internal helpers include queue zapping/flushing, AMPDU garbage collection, interface initialization, power-save update, survey update, EEPROM read, and EEPROM parse.

## Control Flow

Allocation creates an `ieee80211_hw`, preallocates RX stream failover storage, initializes locks, queues, work items, lists, completions, and hardware capability flags. Registration reads EEPROM, parses band/regulatory/MAC data, registers mac80211 hardware, then optional debugfs/LED/WPS/RNG facilities. `start` resets queues/defaults, opens USB, initializes MAC/QoS/RX filter/DMA, clears key cache, marks the device started, schedules stats, and wakes queues. `stop` moves to idle, stops queues/DMA/USB, zaps queues, and cancels workers. Restart work tries USB restart or full USB reset, then calls `ieee80211_restart_hw()` on success.

## State and Persistence Behavior

This file owns long-lived driver state: VIF bitmap/list, main/slave interface selection, beacon SKBs, queue statistics, TX pending/status queues, aggregation TID structures, key bitmap, filter state, power-save state, survey array, noise defaults, EEPROM copy, regulatory state, registered flag, pending restart count, module-parameter-driven HT/crypto behavior, optional RNG cache, and delayed work scheduling.

## Dependencies and Integration Points

It integrates with mac80211/cfg80211, ath regulatory helpers, USB transport, command execution, TX/RX paths, beacon/CAB helpers, MAC/PHY programming, debugfs, LEDs, input WPS button support, hwrng, Linux workqueues, RCU, mutexes, spinlocks, completions, and SKB queues.

## Risks and Edge Cases

Multi-interface support is constrained by a single hardware main mode plus ACK-table slave entries. Hardware crypto falls back for IBSS, non-main VIFs, P2P, unsupported ciphers, and exhausted key slots. AMPDU cleanup relies on RCU and delayed garbage collection. `carl9170_flush()` waits up to one second for uploaded frames to complete. Restart scheduling must avoid duplicate resets using `pending_restarts`.

## Test Signals

Run mac80211 start/stop, suspend stop, USB restart/failure, interface add/remove combinations, AP/STA/mesh/IBSS mode changes, power-save toggles, channel changes, filter changes, BSS changes, key install/remove, AMPDU start/stop/operational, survey reads, stats reads, flush with and without drop, registration failure unwinds, and unregister/free leak checks. Build with `noht`, `nohwcrypt`, debugfs, LED, WPS, and HWRNG configurations.
