# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-at91-core.c

## Purpose
Shared platform-driver core for the Atmel/Microchip AT91 TWI controller. It owns resource discovery, compatible-to-capability selection, adapter registration, runtime/system PM, and mode dispatch between the master implementation in `i2c-at91-master.c` and optional slave implementation in `i2c-at91-slave.c`.

## APIs, Control Flow, and State
Important shared helpers are `at91_twi_read()`, `at91_twi_write()`, `at91_disable_twi_interrupts()`, `at91_twi_irq_save()`, `at91_twi_irq_restore()`, and `at91_init_twi_bus()`. `at91_twi_probe()` allocates `struct at91_twi_dev`, maps MMIO, gets IRQ and clock, fills `struct i2c_adapter`, detects slave mode with `i2c_detect_slave_mode()`, calls `at91_twi_probe_master()` or `at91_twi_probe_slave()`, resets/initializes hardware, enables runtime autosuspend, and registers a numbered adapter. Device-specific `struct at91_twi_pdata` entries encode clock divider limits and feature flags for UNRE, alternative command mode, HOLD, digital/analog filters, FIFO-related behavior, and the CLEAR bus recovery command.

## Dependencies and Integration
Integrates with platform bus, OF match tables, legacy platform IDs, Linux I2C core, clk, pinctrl sleep/default states, and runtime PM. Its exported state is in `struct at91_twi_dev`, which is consumed by the master/slave compilation units through `i2c-at91.h`.

## Risks and Test Signals
Risk centers on SoC capability mismatches, PM sequencing, and wrong master/slave dispatch. Test with DT compatibles across AT91/SAMA5/SAM9x60 variants, runtime suspend/resume, system suspend_noirq/resume_noirq, missing clocks/IRQs, slave-mode DT detection, and adapter add/remove. Failures show as incorrect bus speed/features, lost register state after resume, or probe deferral/resource leaks.
