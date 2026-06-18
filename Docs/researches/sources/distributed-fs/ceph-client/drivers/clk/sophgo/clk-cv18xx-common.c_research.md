# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-common.c

## Purpose
This file provides shared low-level register helpers for CV18xx clock classes. It centralizes locked bit set/clear operations, unlocked bit checks, and PLL lock polling.

## Important APIs, Types, And Functions
`cv1800_clk_setbit()` and `cv1800_clk_clearbit()` perform spinlock-protected read-modify-write operations on a single bit described by `struct cv1800_clk_regbit`. `cv1800_clk_checkbit()` reads a bit without taking the shared lock. `cv1800_clk_wait_for_lock()` polls a status register until a lock mask is set, warning after `PLL_LOCK_TIMEOUT_US` microseconds.

## Control Flow
Set and clear helpers save IRQ flags, read `common->base + field->reg`, modify `BIT(field->shift)`, write back, and release the lock. Lock polling returns immediately when the requested mask is zero; otherwise it uses `readl_relaxed_poll_timeout()` with a 100 microsecond interval and 200 millisecond timeout.

## State And Persistence
The functions mutate MMIO registers and rely on `struct cv1800_clk_common` having already been initialized with the controller base and shared lock. There is no separately allocated state.

## Dependencies And Integration Points
These helpers are used by CV18xx gate, divider, mux, audio, and PLL ops. They depend on Linux MMIO, polling, spinlock, and warning facilities, plus field descriptors from `clk-cv18xx-common.h`.

## Risks
`cv1800_clk_checkbit()` is intentionally unlocked, so callers that make decisions from it can race with concurrent set/clear paths. Poll timeout only warns; callers continue after a failed lock, which may leave clocks at unexpected rates. All helpers assume `common->lock` is valid before any CCF operation is invoked.

## Test Signals
Unit-style register tests can use fake MMIO to validate set/clear masks. Hardware tests should force PLL rate changes and confirm lock status polling succeeds and warning paths are observable when hardware fails to lock.
