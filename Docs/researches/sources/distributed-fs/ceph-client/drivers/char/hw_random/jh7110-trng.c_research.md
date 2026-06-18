# sources/distributed-fs/ceph-client/drivers/char/hw_random/jh7110-trng.c

## Purpose
This driver supports the StarFive JH7110 TRNG. It manages clocks, reset, IRQ completions for random/reseed events, auto-reseed parameters, runtime PM, and reads 128- or 256-bit random blocks.

## Important APIs, Types, and Functions
- `struct starfive_trng` stores device, MMIO, clocks, reset, hwrng, completions, mode/reseed settings, and a spinlock for control writes.
- Module parameters `autoreq` and `autoage` configure automatic reseeding thresholds.
- `starfive_trng_init()` programs auto-reseed, interrupts, mode, and performs initial reseed.
- `starfive_trng_cmd()` writes commands and waits for completion.
- `starfive_trng_irq()` completes random/reseed events and triggers reseed on LFSR lockup.
- `starfive_trng_read()` waits idle, generates random data, and copies result registers.

## Control Flow
Probe maps resources, requests IRQ, gets clocks/reset, enables hardware, initializes runtime PM, and registers hwrng. Core init enables interrupts, programs 256-bit mode by default, and reseeds. Reads resume runtime PM, cap maximum length by mode, optionally wait for idle, issue generate command, copy registers, and autosuspend.

## State and Persistence Behavior
Mode, mission, reseed, autoage, and autoreq persist in software/registers. Completions synchronize IRQ-driven command completion. Runtime PM controls clocks; cleanup asserts reset and disables clocks.

## Dependencies and Integration Points
It depends on OF compatible `starfive,jh7110-trng`, platform IRQ/MMIO, clocks `hclk` and `ahb`, reset controller, runtime PM, and hwrng core.

## Risks
`starfive_trng_read()` returns early on errors without putting the runtime PM reference, which can leak PM usage. IRQ handler writes reseed command on LFSR lockup without reinitializing completion. Module parameters are global rather than per device.

## Test Signals
Test initial reseed timeout, random generation timeout with `wait` false/true, PM reference balancing on error paths, LFSR lockup IRQ, suspend/resume, clock/reset failures, and 128/256-bit mode behavior.
