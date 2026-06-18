# sources/distributed-fs/ceph-client/drivers/gpio/gpio-xgene.c

## Purpose
Provides the main AppliedMicro X-Gene SoC GPIO controller driver for up to 48 GPIOs in three banks, with simple MMIO direction/value handling and suspend/resume context save.

## Important APIs, Types, And Functions
- `struct xgene_gpio` stores the gpiochip, MMIO base, spinlock, and saved `SET_DR` register values for three banks.
- `xgene_gpio_get`, `xgene_gpio_set`, `xgene_gpio_get_direction`, `xgene_gpio_dir_in`, and `xgene_gpio_dir_out` implement gpiolib operations using bank and bit macros.
- `__xgene_gpio_set` updates the output bit portion of the `GPIO_SET_DR_OFFSET` register.
- `xgene_gpio_suspend` and `xgene_gpio_resume` save and restore the three direction/output registers.
- `xgene_gpio_probe` maps the resource, initializes callbacks, and registers the chip.

## Control Flow
GPIO offsets are split into 16-line banks. Direction state lives in the low 16 bits of each bank's set/direction register, where set means input and clear means output. Output state uses the corresponding bit shifted by 16. Direction-output clears the direction bit and writes the value while holding the spinlock. Suspend copies each bank's `SET_DR` register into `set_dr_val`; resume writes them back.

## State And Persistence
The only software state beyond the spinlock is the suspend context array. Hardware registers hold live direction and output state. The driver is built in via `builtin_platform_driver` and has no remove path.

## Dependencies And Integration Points
Depends on platform MMIO resources, OF compatible `apm,xgene-gpio`, optional ACPI ID `APMC0D14`, gpiolib, and system sleep PM hooks.

## Risks And Edge Cases
No IRQ support is provided in this main controller. The set/direction register packs direction and output bits, so careless read-modify-write can corrupt direction while changing value. `ngpio` is fixed at 48 with no property override. Suspend/resume assumes all three banks exist and remain powered consistently.

## Test Signals
Verify bank/bit calculations at offsets 15/16/31/32/47, direction bit polarity, output value bit shift by 16, spinlocked RMW sequences, ACPI and OF binding, and suspend/resume restoration of all bank registers.
