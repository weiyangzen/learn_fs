# sources/distributed-fs/ceph-client/drivers/mfd/twl4030-irq.c

## Purpose
`twl4030-irq.c` implements two-stage interrupt support for TWL4030/TWL5030/TPS659x0-class chips. It demultiplexes the primary interrupt handler (PIH) status into secondary interrupt handler (SIH) modules, configures nested Linux IRQs for core and power interrupts, supports SIH mask and edge-trigger programming over sleeping I2C operations, and selects TWL4030 versus TWL5031 SIH tables.

## Important APIs, Types, And Functions
Important structures are `struct sih`, describing hardware SIH modules, and `struct sih_agent`, tracking a Linux nested IRQ bank. Static SIH tables are `sih_modules_twl4030[]` and `sih_modules_twl5031[]`. Main functions are `twl4030_init_chip_irq()`, `twl4030_init_irq()`, `twl4030_sih_setup()`, `handle_twl4030_pih()`, `handle_twl4030_sih()`, `twl4030_init_sih_modules()`, and `twl4030_exit_irq()`. IRQ-chip methods are `twl4030_sih_mask()`, `twl4030_sih_unmask()`, `twl4030_sih_set_type()`, and bus lock/sync-unlock.

## Control Flow
`twl-core.c` first calls `twl4030_init_chip_irq()` to choose the SIH table. `twl4030_init_irq()` allocates descriptors for PIH plus PWR_INT, creates a legacy domain, masks and clears SIH modules, installs dummy handlers for core PIH-level IRQs, sets up the PWR_INT SIH bank, requests a threaded parent IRQ, and enables wake. The parent handler reads PIH ISR and dispatches nested PIH IRQs. For SIH modules, threaded handlers read ISR bytes, acknowledge via clear-on-read where configured, and dispatch nested child IRQs.

## State, Persistence, And Dependencies
Global state includes `irq_line`, `sih_modules`, `nr_sih_modules`, and `twl4030_irq_base`. Each `sih_agent` stores mask bits, pending mask changes, pending edge changes, and a mutex. Persistent hardware effects include SIH mask writes, SIH control COR configuration, EDR edge-trigger writes, and pending interrupt clearing. Dependencies include TWL core I2C helpers, Linux irqdomain/nested IRQ APIs, threaded IRQs, and register/module constants from `linux/mfd/twl.h`.

## Integration Points
The TWL core invokes this file for TWL4030-class parent IRQ setup and teardown. Other TWL child drivers can call `twl4030_sih_setup()` to configure a SIH bank such as GPIO. The initial core setup always configures PWR_INT after the PIH bank.

## Risks
`twl4030_exit_irq()` is effectively unimplemented and logs inability to clean up. `twl4030_sih_setup()` allocates `sih_agent` and `irq_name` without a corresponding teardown path. IRQ descriptor/domain cleanup is incomplete on several failure paths. Edge registers are shared across interrupt lines and are read-modify-written without cross-line coordination. Only line 0 is used (`twl_irq_line`). Some SIH modules such as USB are skipped because they do not follow the standard organization.

## Test Signals
Test TWL4030 and TWL5031 table selection, initial mask/COR/clear writes, parent PIH dispatch for each module bit, PWR_INT nested dispatch, SIH mask/unmask bus sync, rising/falling/both edge programming, invalid trigger rejection, I2C error handling, wake enable, and cleanup/reprobe behavior.
