# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/util.h

## Purpose
Declares shared mt76 utility types and inline helpers for WCID bitmaps, SKB More Data bit manipulation, ring-index incrementing, and kthread worker lifecycle.

## Important APIs, Types, And Functions
Defines `struct mt76_worker`, worker state bits `MT76_WORKER_SCHEDULED` and `MT76_WORKER_RUNNING`, `MT76_INCR()`, `mt76_wcid_mask_set()`, `mt76_wcid_mask_clear()`, `mt76_skb_set_moredata()`, and inline worker helpers `mt76_worker_setup()`, `mt76_worker_schedule()`, `mt76_worker_disable()`, `mt76_worker_enable()`, and `mt76_worker_teardown()`.

## Control Flow
Worker setup creates a named kthread running `__mt76_worker_fn()`. Scheduling sets the scheduled bit and wakes the task unless already running. Disable parks the kthread and clears state; enable unparks and schedules it; teardown stops the thread. More Data helper directly toggles the 802.11 frame-control bit in an SKB header.

## State And Persistence
Worker state is held in the task pointer, callback pointer, and state bits. WCID bitmap helpers mutate caller-owned bitmaps. SKB frame control is modified in place.

## Dependencies And Integration Points
Depends on Linux SKB, bitops, bitfield, mac80211, wiphy names, and the implementation of `__mt76_worker_fn()` in `util.c`. Used by generic TX, USB, SDIO, and chip-specific worker paths.

## Risks
`mt76_worker_schedule()` coalesces events while RUNNING, so callbacks must drain all available work. `mt76_skb_set_moredata()` assumes the SKB data starts with an 802.11 header. Disable/enable must not race with object destruction.

## Test Signals
Correct worker names, scheduling after enable, no wake after teardown, correct More Data bit in PS-buffered frames, and WCID bitmap set/clear consistency.
