# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-nomadik.c

## Purpose
Implements the AMBA Nomadik/Ux500 I2C master adapter, with Mobileye EyeQ5/EyeQ6H compatibility hooks. It exposes a kernel `i2c_adapter` for Nomadik-family controllers, programs the controller clock/FIFO thresholds, drives interrupt-based master transfers, and handles runtime/system power transitions.

## Important APIs, Types, And Functions
Core state is held in `struct nmk_i2c_dev`, which owns AMBA device metadata, MMIO base, clock, current `i2c_nmk_client`, FIFO thresholds, transfer wait queue, timeout, result, and 32-bit-bus access mode. `nmk_i2c_xfer()` is the adapter `.xfer` implementation; `nmk_i2c_xfer_one()`, `read_i2c()`, and `write_i2c()` program `I2C_MCR`, `I2C_CR`, and interrupt masks for each message. `i2c_irq_handler()` drains/fills FIFOs and completes transfers. Probe/remove are `nmk_i2c_probe()` and `nmk_i2c_remove()`, registered through `amba_driver`.

## Control Flow
Probe reads firmware properties, applies EyeQ OLB speed setup when matched, maps registers, requests IRQ, enables the clock, initializes hardware, builds the adapter, and registers it. A transfer runtime-resumes the device, retries the message list up to three times, calls `setup_i2c_controller()`, loads per-message client state, executes read/write, and waits on `xfer_wq`. The IRQ handler processes one pending interrupt source, moves bytes through TX/RX FIFOs, records errors on arbitration/bus/FIFO conditions, disables/clears interrupts on transaction done, and wakes the waiter.

## State And Persistence
Persistent runtime state is device-local in `struct nmk_i2c_dev`; no on-disk state exists. Hardware state spans CR/MCR/BRCR/FIFO/interrupt registers and is reset by `init_hw()`. Runtime PM gates the controller clock and restores default hardware state on resume. EyeQ5 speed-mode selection persists in an external syscon regmap until changed by firmware or another driver.

## Dependencies And Integration Points
Depends on AMBA, Linux I2C core, runtime PM, clocks, pinctrl PM states, device tree properties, syscon/regmap for EyeQ5, and IRQ delivery. It advertises `I2C_FUNC_I2C`, SMBus emulation, and 10-bit addressing. It integrates early with `subsys_initcall()` because I2C can be needed during platform bring-up.

## Risks
Timeout handling and FIFO accounting are critical: stale `cli.count`, missed `MTD/MTDWS`, or an unhandled interrupt can leave the bus stuck. The IRQ handler processes only the first set bit in `MISR`, so simultaneous status bits rely on later interrupts. EyeQ 32-bit access mode and OLB speed masks must match the actual SoC. Runtime PM failures can leave clocks disabled while callers expect transfers.

## Test Signals
Useful signals are successful `i2cdetect`/SMBus transfers across 100 kHz, 400 kHz, fast-plus, and high-speed modes; repeated-start write-read transactions; 10-bit address smoke tests; timeout injection with absent targets; suspend/resume and runtime autosuspend cycles; IRQ error logging for arbitration/bus errors; and EyeQ5/EyeQ6H boot tests that confirm the correct MMIO access width and OLB speed selection.
