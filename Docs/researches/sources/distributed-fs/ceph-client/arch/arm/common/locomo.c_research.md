<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/locomo.c -->
# sources/distributed-fs/ceph-client/arch/arm/common/locomo.c

## Purpose
Core driver and bus implementation for Sharp LoCoMo companion chips used by older Sharp handhelds. It initializes the chip, cascades interrupts, creates child devices, and exports GPIO, DAC, and frontlight helpers.

## Important APIs/types/functions
- Core state: `struct locomo` with device, physical base, IRQ, IRQ base, lock, I/O base, and saved PM state.
- Child description: `struct locomo_dev_info locomo_devices[]`.
- IRQ path: `locomo_handler()`, `locomo_mask_irq()`, `locomo_unmask_irq()`, `locomo_setup_irq()`.
- Probe/remove/PM: `__locomo_probe()`, `locomo_probe()`, `locomo_suspend()`, `locomo_resume()`, `__locomo_remove()`.
- Exported helpers: `locomo_gpio_set_dir()`, `locomo_gpio_read_level()`, `locomo_gpio_read_output()`, `locomo_gpio_write()`, `locomo_m62332_senddata()`, `locomo_frontlight_set()`, `locomo_driver_register()`, and `locomo_driver_unregister()`.
- Bus type: `locomo_bus_type`.

## Control flow
Platform probe maps the MMIO page, clears interrupt/GPIO/frontlight/SPI state, initializes timing/DAC registers, reads version, installs a chained interrupt handler if IRQ resources exist, and registers child devices on the LoCoMo bus. Interrupt handling acknowledges the parent, reads request bits from `LOCOMO_ICR`, and dispatches up to four child IRQs. PM suspend saves selected registers and powers down outputs/clocks; resume restores state and reinitializes keyboard clocking. Child drivers bind through the custom bus by matching `devid`.

## State and persistence behavior
Runtime state lives in the mapped LoCoMo registers, child `struct device` instances, `saved_state` allocated across suspend, and spinlock-protected GPIO/DAC/frontlight access. There is no disk persistence.

## Dependencies and integration points
Depends on platform data for IRQ base, `asm/hardware/locomo.h` register definitions, platform resources, the driver core, chained IRQ handling, and Sharp handheld child drivers for keyboard, frontlight, backlight, audio, LED, UART, and SPI.

## Risks and edge cases
Legacy custom bus and platform-data-only discovery limit DT/ACPI integration. The bit-banged DAC path holds the spinlock across many `udelay()` calls. Child registration errors are mostly not propagated after probe starts. IRQ base handling uses legacy static IRQ assumptions. Suspend/resume saves only selected registers, so child drivers must restore their own state.

## Test signals
Boot a LoCoMo-based Sharp platform, verify child devices bind, trigger keyboard/GPIO/SPI interrupts, exercise frontlight/DAC helpers, and run suspend/resume. Build with `CONFIG_SHARP_LOCOMO`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/common/locomo.c -->
