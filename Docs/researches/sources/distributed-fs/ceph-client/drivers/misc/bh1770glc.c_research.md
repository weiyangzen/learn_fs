# sources/distributed-fs/ceph-client/drivers/misc/bh1770glc.c

## Purpose
`bh1770glc.c` is an I2C driver for ROHM BH1770GLC and OSRAM SFH7770 combined ambient-light and proximity sensors. It powers the chip, detects the variant, exposes lux and proximity controls through sysfs, handles runtime/system PM, and processes sensor interrupts.

## Important APIs, Types, and Functions
The central state is `struct bh1770_chip`, containing platform data, regulators, mutex, waitqueue, IRQ/work state, lux calibration/rate/threshold fields, and proximity threshold/rate/persistence fields. Probe/remove are `bh1770_probe()` and `bh1770_remove()`. PM callbacks are `bh1770_suspend()`, `bh1770_resume()`, `bh1770_runtime_suspend()`, and `bh1770_runtime_resume()`. Device control helpers include `bh1770_chip_on()`, `bh1770_chip_off()`, `bh1770_detect()`, `bh1770_lux_rate()`, `bh1770_lux_update_thresholds()`, `bh1770_lux_read_result()`, `bh1770_prox_mode_control()`, and `bh1770_prox_read_result()`. `bh1770_irq()` is the threaded IRQ handler.

## Control Flow
Probe allocates state, requires platform data, initializes defaults, gets and temporarily enables regulators, detects manufacturer/part, starts the chip, enables runtime PM, computes correction factors, creates sysfs attributes, requests a threaded level/falling IRQ, then disables regulators for idle. Writing `power_state` resumes runtime PM, configures lux rate/interrupts, primes thresholds, waits for the first ALS result, and applies proximity mode if enabled. IRQ handling reads ALS/proximity status, acknowledges by reading interrupt control, updates raw lux and wakes waiters, temporarily disables interrupt logic, notifies sysfs on lux/proximity changes, calls proximity filtering, restores interrupt enables, and schedules delayed work to synthesize a missing no-proximity transition.

## State and Persistence
All state is in memory. Runtime PM controls regulator state and chip register programming. Lux correction combines platform glass attenuation, chip factor, and sysfs calibration. Proximity state tracks enable refcount, persistence counter, adjusted result, hardware threshold, absolute threshold, and separate rates above/below threshold. Sysfs writes persist only until driver removal.

## Dependencies and Integration Points
The driver depends on I2C SMBus operations, regulator bulk APIs, platform data from `linux/platform_data/bh1770glc.h`, sysfs device attributes, threaded IRQs, delayed work, waitqueues, and runtime PM. It does not use the modern IIO subsystem; user space consumes sensor values through legacy sysfs names such as `lux0_input` and `prox0_raw`.

## Risks and Edge Cases
Many I2C writes during mode changes ignore individual return values. Some sysfs setters, including proximity persistence and absolute threshold, update state without taking `chip->mutex`. `bh1770_lux_read_result()` ignores the return from `bh1770_lux_get_result()` before converting cached raw data. Proximity readings are suppressed above a fixed lux raw limit, which may hide real near events under bright light. Probe powers on, enables runtime PM, and then disables regulators manually, so PM state must remain consistent.

## Test Signals
Validation should cover probe with both manufacturer IDs, missing platform data, regulator failures, runtime suspend/resume, system suspend/resume with enabled sensors, lux wait timeout, threshold sysfs updates while powered off/on, proximity persistence filtering, IRQ notification paths, delayed no-proximity work, and calibration values that would produce zero correction.
