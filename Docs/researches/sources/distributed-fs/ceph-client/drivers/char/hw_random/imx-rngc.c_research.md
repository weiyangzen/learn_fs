# sources/distributed-fs/ceph-client/drivers/char/hw_random/imx-rngc.c

## Purpose
This driver supports Freescale i.MX RNGC/RNGB hardware. It validates the RNG type, optionally runs self-test, seeds the generator with interrupt completion, enables automatic reseeding, reads FIFO words, and manages clocks through runtime PM.

## Important APIs, Types, and Functions
- `struct imx_rngc` stores device, clock, MMIO base, hwrng, operation completion, and error register snapshot.
- `imx_rngc_irq_mask_clear()` and `imx_rngc_irq_unmask()` manage done/error interrupts and clear status.
- `imx_rngc_self_test()` runs hardware self-test.
- `imx_rngc_init()` clears errors, seeds repeatedly until statistical errors stop, enables auto-seed, and leaves interrupts unmasked.
- `imx_rngc_read()` drains FIFO words under runtime PM.
- `imx_rngc_irq()` snapshots status/error, masks/clears, and completes seed/self-test events.

## Control Flow
Probe maps MMIO, enables clock, verifies version type, initializes completion, masks interrupts, requests IRQ, optionally self-tests, enables runtime PM, and registers hwrng. Core init performs seed creation and auto-seed setup. Reads resume the device, pull FIFO words until empty/error, and autosuspend.

## State and Persistence Behavior
`err_reg` stores the last interrupt error while interrupts are masked. Hardware seed and auto-seed configuration persist while selected. Clock state is runtime-PM controlled.

## Dependencies and Integration Points
It depends on OF compatible `fsl,imx25-rngb`, platform IRQ/MMIO, clocks, runtime PM, hwrng core, and module parameter `self_test`.

## Risks
The read path returns `-EIO` when no word is available even if `wait` is false. Init loops on statistical seed errors and can timeout. Correct interrupt masking is critical because clearing interrupts can also clear error information.

## Test Signals
Test unsupported RNG type, self-test pass/fail/timeout, seed statistical retry, FIFO empty/error reads, runtime suspend/resume, IRQ completion, and cleanup masking.
