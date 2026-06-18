# sources/distributed-fs/ceph-client/drivers/mfd/retu-mfd.c

## Purpose
`retu-mfd.c` is the Nokia Retu/Tahvo I2C MFD core. It wraps a 16-bit SMBus register protocol in regmap, exposes synchronized read/write helpers, sets up variant-specific IRQ chips, registers child devices, and provides Retu poweroff through the watchdog.

## Important APIs, Types, And Functions
`struct retu_dev` stores regmap, device, mutex, and IRQ data. Exported APIs are `retu_read()` and `retu_write()`. `retu_bus` supplies custom regmap read/write callbacks over SMBus word operations. `retu_irq_chip` and `tahvo_irq_chip` describe power-button and VBUS interrupts. `retu_probe()`, `retu_remove()`, and `retu_power_off()` implement lifecycle.

## Control Flow
Probe chooses Retu or Tahvo data from I2C address, allocates state, initializes custom regmap, reads ASIC revision, masks all interrupts, adds a regmap IRQ chip, registers variant children with IRQ base from regmap-irq, and for Retu installs `pm_power_off` if free. Poweroff sets a control bit to ignore power-button state, writes watchdog zero, and loops forever waiting for shutdown.

## State And Persistence
The driver serializes all register access with a mutex. Hardware interrupt masks, watchdog, and power-control registers persist until changed or poweroff occurs. A global `retu_pm_power_off` tracks the Retu device owning `pm_power_off`.

## Dependencies And Integration Points
It depends on I2C SMBus word transfers, custom regmap bus support, regmap-irq, MFD core, `linux/mfd/retu.h`, OF/I2C IDs for `nokia,retu` and `nokia,tahvo`, and children `retu-wdt`, `retu-pwrbutton`, and `tahvo-usb`.

## Risks
Variant selection by I2C address (`addr - 1`) is unusual and assumes board layout. The custom regmap callbacks use `BUG_ON()` for size contract violations. Poweroff loops forever after watchdog write. Remove clears global `pm_power_off` unconditionally for the owner, so multi-poweroff interactions must be considered.

## Test Signals
Probe both Retu and Tahvo addresses, read ASIC revision, power-button and VBUS IRQ delivery, child IRQ bases, exported read/write serialization, poweroff behavior on Retu, remove cleanup, and SMBus error handling.
