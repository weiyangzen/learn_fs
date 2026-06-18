# sources/distributed-fs/ceph-client/drivers/mfd/stmfx.c

## Purpose
`stmfx.c` is the I2C MFD core for STMicroelectronics STMFX-0300 multifunction expander. It manages the chip regmap, optional VDD supply, function enable/disable arbitration, nested interrupts, reset, suspend/resume restore, and child devices for pinctrl, IDD measurement, and touchscreen.

## Important APIs, Types, and Functions
Regmap callbacks are `stmfx_reg_volatile()` and `stmfx_reg_writeable()`. Exported function controls are `stmfx_function_enable()` and `stmfx_function_disable()`. IRQ functions include `stmfx_irq_handler()`, `stmfx_irq_map()`, `stmfx_irq_init()`, and `stmfx_irq_exit()`. Chip lifecycle functions are `stmfx_chip_init()`, `stmfx_chip_reset()`, `stmfx_chip_exit()`, `stmfx_probe()`, `stmfx_remove()`, `stmfx_suspend()`, and `stmfx_resume()`.

## Control Flow
Probe creates an 8-bit regmap, initializes the mutex, enables optional VDD, verifies chip ID against the I2C address, reads firmware version, resets the chip, configures the IRQ output pin from DT and parent IRQ trigger, requests a threaded IRQ, creates an IRQ domain, and registers three MFD cells with IRQ resources. The threaded handler reads pending sources, ACKs non-GPIO sources, and dispatches nested IRQs.

## State and Persistence
`struct stmfx` stores the regmap, IRQ domain, cached IRQ source mask, locks, optional regulator, and suspend backups for SYS_CTRL and IRQ_OUT_PIN. Suspend backs up selected registers, disables the IRQ, and may disable VDD. Resume re-enables VDD, resets the chip, restores backed-up registers and `irq_src`, then re-enables the IRQ.

## Dependencies and Integration Points
It depends on I2C, regmap with maple cache, regulator framework, irqdomain, nested threaded IRQ handling, and child drivers compatible with `st,stmfx-0300-pinctrl`, `st,stmfx-0300-idd`, and `st,stmfx-0300-ts`.

## Risks and Edge Cases
Function conflicts are enforced in software because IDD/TS firmware behavior can disable ALTGPIO. GPIO pending has no direct ACK and is represented by a logical OR of GPIO pending banks. Resume resets the chip, so all necessary state must be backed up or reconfigured by children. Probe defers only when chip init returns `-ETIMEDOUT`.

## Test Signals
Validate chip ID/address matching, firmware logging, function conflict rejection, nested IRQ delivery for GPIO/IDD/TS sources, open-drain and polarity configuration, suspend/resume with regulator off, and child drivers reusing exported function controls.
