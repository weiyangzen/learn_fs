# sources/distributed-fs/ceph-client/drivers/char/hw_random/ba431-rng.c

## Purpose
This driver supports Silex Insight BA431 TRNG IP. It resets/enables the IP, reads words from its FIFO, detects hardware error states, and schedules asynchronous reset work when errors are seen during reads.

## Important APIs, Types, and Functions
- `enum ba431_state` describes reset/startup/running/error states from the status register.
- `struct ba431_trng` stores device, MMIO base, hwrng, reset-pending flag, and reset work.
- `ba431_trng_reset()` soft-resets the IP, enables it, and polls until it leaves error/reset state.
- `ba431_trng_read()` drains FIFO words and schedules reset on empty/error conditions.
- `ba431_trng_cleanup()` disables the IP and cancels reset work.

## Control Flow
Probe maps MMIO, initializes reset work, installs hwrng callbacks, and registers. Core init runs a reset. Reads check FIFO level; if empty and in error, they schedule reset and return partial data. If waiting and not in error, they delay briefly and retry. After reading a FIFO batch, the code rechecks state before accepting those words.

## State and Persistence Behavior
The driver maintains one atomic `reset_pending` to avoid duplicate reset work. Hardware enable and softreset bits persist until cleanup. FIFO contents are transient and not buffered in software.

## Dependencies and Integration Points
It depends on OF compatible `silex-insight,ba431-rng`, platform MMIO, workqueues, hwrng core, and polling helpers.

## Risks
The final byte count calculation uses `n *= sizeof(data)`, where `data` is a pointer variable; on 64-bit this reports 8 bytes per word instead of 4. Error recovery is asynchronous, so reads may return short data while reset work is pending.

## Test Signals
Test reset success/timeout, FIFO-empty blocking/nonblocking reads, error-state reset scheduling, cleanup canceling work, and byte-count correctness on 32-bit and 64-bit builds.
