# sources/distributed-fs/ceph-client/drivers/mfd/ti-lmu.c

## Purpose
`ti-lmu.c` is the I2C MFD core for TI Lighting Management Unit devices. It powers up the chip, creates a shared regmap, initializes a fault notifier, and registers regulator, backlight, LED, and fault-monitor child devices according to chip family.

## Important APIs, Types, and Functions
`struct ti_lmu_data` stores chip-specific child cells and maximum register. `ti_lmu_enable_hw()` drives the optional enable GPIO and applies the LM3631 LCD_EN sequence. `ti_lmu_disable_hw()` is the devm cleanup action. `ti_lmu_probe()` selects match data, initializes the regmap, enables hardware, initializes the blocking notifier, and registers children.

## Control Flow
Probe gets OF match data, allocates `struct ti_lmu`, builds an 8-bit regmap config named after the I2C ID, requests optional enable GPIO high, waits for hardware, performs any chip-specific power-up sequence, registers a cleanup action to turn the GPIO off, initializes the fault notifier head, stores client data, and registers chip-specific MFD cells.

## State and Persistence
State is the parent `struct ti_lmu`: device, regmap, optional enable GPIO, and notifier chain. Child drivers own functional register programming. The cleanup action disables the hardware enable GPIO on detach or failed later probe.

## Dependencies and Integration Points
It depends on I2C, GPIO descriptors, regmap, TI LMU headers/register definitions, and children such as `ti-lmu-backlight`, `lm363x-regulator`, `lm3633-leds`, `lm36274-leds`, and `ti-lmu-fault-monitor`.

## Risks and Edge Cases
Probe requires OF match data even though I2C IDs are present. `id->driver_data` is used for the LM3631 special sequence and assumes a matching I2C ID is available. Enable GPIO is requested initially high before `ti_lmu_enable_hw()` sets it again. Child set varies significantly by compatible.

## Test Signals
Validate each compatible's child list and max register, optional enable GPIO sequencing and cleanup, LM3631 LCD_EN update, notifier availability to fault-monitor children, and regmap access bounds.
