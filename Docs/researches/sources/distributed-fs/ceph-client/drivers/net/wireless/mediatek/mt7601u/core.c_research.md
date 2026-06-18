# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt7601u/core.c

## Purpose
Provides low-level readiness and polling helpers for the legacy MT7601U driver.

## Important APIs, Types, And Functions
`mt7601u_wait_asic_ready()` polls `MT_MAC_CSR0` until the chip returns a valid nonzero/non-all-ones value. `mt76_poll()` and `mt76_poll_msec()` poll arbitrary registers using microsecond or 10 ms sleep intervals and abort if `MT7601U_STATE_REMOVED` is set.

## Control Flow
All helpers repeatedly read registers, compare masked values, delay, and fail on timeout or removal. Poll helpers log timeout register addresses.

## State And Persistence
They read hardware registers and device removal state. No persistent driver state is written.

## Dependencies And Integration Points
Used during probe, hardware init, MAC start/stop, efuse reads, and reset flows throughout mt7601u. Depends on `mt7601u_rr()` register access and state bits.

## Risks
Timeout values are caller-selected and may be too short for slow USB devices or firmware states. A removed device forces false/EIO to prevent further USB access.

## Test Signals
Probe readiness after USB attach, timeout logging on unplug/stall, and successful waits around DMA idle, MAC idle, and efuse kick completion.
