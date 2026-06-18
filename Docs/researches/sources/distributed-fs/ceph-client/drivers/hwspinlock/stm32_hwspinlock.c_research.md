# sources/distributed-fs/ceph-client/drivers/hwspinlock/stm32_hwspinlock.c

## Purpose
This provider driver exposes STM32 hardware semaphores as 32 generic hardware spinlocks.

## Important APIs, Types, And Functions
- `struct stm32_hwspinlock` stores the semaphore clock and embedded hwspinlock bank.
- `stm32_hwspinlock_trylock()` writes lock bit plus core ID and succeeds only if the register reads back the same value.
- `stm32_hwspinlock_unlock()` writes the core ID without the lock bit.
- `stm32_hwspinlock_relax()` delays 50 ns.
- Runtime PM callbacks disable and enable the semaphore clock.
- `stm32_hwspinlock_probe()` maps MMIO, enables the `hsem` clock, initializes runtime PM, stores per-lock register addresses, and registers the bank.

## Control Flow
Probe maps the register block, allocates the bank, gets/prepares/enables the clock, marks the device runtime-active, registers a devm cleanup action for runtime PM and clock teardown, fills 32 `priv` MMIO pointers, and calls `devm_hwspin_lock_register()`. Registration is performed from `postcore_initcall`.

## State And Persistence
The driver stores only clock and bank state. Runtime PM gates the clock according to core request/free activity. Hardware lock ownership is encoded in each semaphore register using lock bit and core ID.

## Dependencies And Integration Points
It depends on platform MMIO, OF compatible `st,stm32-hwspinlock`, clock `hsem`, runtime PM, and the hwspinlock core.

## Risks
- `STM32_MUTEX_COREID` is hard-coded as bit 8, so the driver assumes a fixed Linux core/processor identity for ownership.
- Runtime PM cleanup calls `pm_runtime_get_sync()` without checking its return, which is common in cleanup but can hide suspend/resume errors.
- Base ID and 32-lock count are fixed.

## Test Signals
Validate clock enable/disable, runtime suspend/resume, trylock readback semantics, unlock write, registration failure cleanup, OF matching, and early registration availability for clients.
