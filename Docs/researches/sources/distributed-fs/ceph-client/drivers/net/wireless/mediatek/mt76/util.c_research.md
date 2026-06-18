# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/util.c

## Purpose
Implements small shared mt76 utilities for register polling, WCID bitmap allocation, minimum average RSSI sampling, and the common kthread worker loop used by USB/SDIO/TX paths.

## Important APIs, Types, And Functions
Exports `__mt76_poll()`, `____mt76_poll_msec()`, `mt76_wcid_alloc()`, `mt76_get_min_avg_rssi()`, and `__mt76_worker_fn()`. Poll helpers repeatedly read registers until masked values match. WCID allocation scans a bitmap for the first free index. RSSI sampling walks allocated WCIDs under RCU and uses EWMA signal values. The worker loop responds to schedule, park, and stop states.

## Control Flow
Poll helpers delay in microsecond or millisecond intervals until timeout. `mt76_get_min_avg_rssi()` disables BH, enters RCU, scans the WCID mask, locks RX state for RSSI/inactive counter updates, and returns the most negative active RSSI. `__mt76_worker_fn()` sleeps until scheduled, handles parking, sets RUNNING, calls the worker callback, reschedules cooperatively, and repeats until kthread stop.

## State And Persistence
State touched includes WCID masks, WCID inactive counters, EWMA RSSI values, and `mt76_worker.state` bits. Worker tasks persist until teardown.

## Dependencies And Integration Points
Depends on mt76 register access wrappers, RCU WCID lookups, RX spinlock, Linux kthreads, and `util.h` inline setup/schedule/disable/enable helpers.

## Risks
Polling timeouts can hide hardware stalls if callers ignore false returns. WCID allocation assumes the mask size and requested size match. Worker scheduling intentionally coalesces requests; code needing edge-counted work must keep its own queue.

## Test Signals
Register poll success/failure paths, WCID allocation exhaustion, RSSI values dropping to zero after inactive counts, worker schedule/park/unpark/teardown under load, and no lockdep issues in BH/RCU sections.
