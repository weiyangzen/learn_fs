# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_reset.c

## Purpose
`ccu_reset.c` implements reset-controller operations for reset bits embedded in sunxi-ng CCU registers.

## Important APIs, Types, And Functions
Important callbacks are `ccu_reset_assert()`, `ccu_reset_deassert()`, `ccu_reset_reset()`, `ccu_reset_status()`, and exported `ccu_reset_ops`.

## Control Flow
Assert clears the hardware bit, deassert sets it, reset pulses assert then delays 10 microseconds before deassert, and status inverts hardware convention so reset-controller semantics return true when reset is asserted.

## State And Persistence
State is hardware reset bits protected by the CCU spinlock. No software persistence exists.

## Dependencies And Integration Points
It depends on reset-controller core, MMIO, delay, spinlocks, and reset maps supplied by each provider.

## Risks
The hardware uses active-low reset bits, opposite the reset API expectation. Wrong inversion would make every consumer see or drive reset backwards.

## Test Signals
Test by probing reset consumers, using debug reset controls where available, and verifying peripherals recover after reset pulses.
